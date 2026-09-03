"""Utilidades reutilizables para trabajar con Utility Networks."""

import json
import requests
from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureLayer


def es_utility_network(item, gis, diagnostico=False):
    """
    Determina si un item de Feature Service contiene una Utility Network real.
    """
    coleccion = FeatureLayerCollection(item.url, gis)
    props = coleccion.properties

    if diagnostico:
        print("Claves disponibles en este servicio:")
        print(list(props.keys()))

    return "controllerDatasetLayers" in props or "utilityNetworkLayerId" in props


def get_un_layer_id(item, gis, diagnostico=False):
    """
    Devuelve el layerId de la capa que representa la Utility Network.
    """
    coleccion = FeatureLayerCollection(item.url, gis)
    props = coleccion.properties
    controller = props.get("controllerDatasetLayers", {})

    if diagnostico:
        print("controllerDatasetLayers (crudo):")
        print(json.dumps(controller, indent=2))

    return controller.get("utilityNetworkLayerId")


def get_network_definition(item, gis, diagnostico=False):
    """
    Consulta queryDataElements en el FeatureServer y devuelve el
    dataElement completo de la Utility Network.
    """
    layer_id = get_un_layer_id(item, gis, diagnostico=diagnostico)

    if diagnostico:
        print("layer_id detectado:", layer_id)

    if layer_id is None:
        print("⚠ No se pudo determinar el layerId de la Utility Network.")
        return None

    url = item.url + "/queryDataElements"
    token = gis._con.token
    params = {"layers": layer_id, "f": "json", "token": token}

    respuesta = requests.get(url, params=params, verify=False)
    data = respuesta.json()

    if diagnostico:
        print("Respuesta completa de queryDataElements (recortada):")
        print(json.dumps(data, indent=2)[:3000])

    layer_elements = data.get("layerDataElements", [])
    if not layer_elements:
        print("⚠ No se encontraron layerDataElements en la respuesta.")
        return None

    for elemento in layer_elements:
        if elemento.get("layerId") == layer_id:
            return elemento.get("dataElement", {})

    print(f"⚠ No se encontró el layerId {layer_id} entre los devueltos ({len(layer_elements)} elementos).")
    return None


def resumen_domain_networks(definicion):
    """
    Recibe el dataElement de la Utility Network y devuelve un resumen
    legible de sus domain networks y tiers.
    """
    domain_networks = definicion.get("domainNetworks", [])
    resultado = []

    for dn in domain_networks:
        tiers = [
            {"nombre": t.get("name", "(sin nombre)"), "rank": t.get("rank", "?")}
            for t in dn.get("tiers", [])
        ]
        resultado.append({
            "nombre": dn.get("domainNetworkName", "(sin nombre)"),
            "es_estructura": dn.get("isStructureNetwork", False),
            "tiers": tiers,
        })

    return resultado


def resumen_asset_groups(definicion):
    """
    Recorre los junctionSources y edgeSources de cada domain network y
    devuelve un resumen de sus asset groups y asset types.
    """
    domain_networks = definicion.get("domainNetworks", [])
    resultado = []

    for dn in domain_networks:
        dn_nombre = dn.get("domainNetworkName", "(sin nombre)")
        sources_resumen = []

        for tipo_fuente, clave in [("junction", "junctionSources"), ("edge", "edgeSources")]:
            for source in dn.get(clave, []):
                asset_groups = []
                for ag in source.get("assetGroups", []):
                    asset_types = [
                        {"nombre": at.get("assetTypeName", "(sin nombre)"), "codigo": at.get("assetTypeCode")}
                        for at in ag.get("assetTypes", [])
                    ]
                    asset_groups.append({
                        "nombre": ag.get("assetGroupName", "(sin nombre)"),
                        "codigo": ag.get("assetGroupCode"),
                        "asset_types": asset_types,
                    })

                sources_resumen.append({
                    "tipo": tipo_fuente,
                    "layerId": source.get("layerId"),
                    "sourceId": source.get("sourceId"),
                    "asset_groups": asset_groups,
                })

        resultado.append({"domain_network": dn_nombre, "sources": sources_resumen})

    return resultado


def get_system_layers(item, gis, diagnostico=False):
    """
    Devuelve el diccionario systemLayers de la Utility Network: los ids
    de las tablas internas (reglas, asociaciones, subredes, dirty areas).
    """
    layer_id = get_un_layer_id(item, gis)
    url = f"{item.url}/{layer_id}"
    token = gis._con.token

    respuesta = requests.get(url, params={"f": "json", "token": token}, verify=False)
    data = respuesta.json()

    if diagnostico:
        print("Definición de la capa UN (recortada):")
        print(json.dumps(data, indent=2)[:2000])

    return data.get("systemLayers", {})


def get_connectivity_rules(item, gis, diagnostico=False):
    """
    Consulta la tabla de reglas de conectividad de la Utility Network
    y devuelve sus registros como una lista de diccionarios.
    """
    system_layers = get_system_layers(item, gis, diagnostico=diagnostico)
    rules_id = system_layers.get("rulesTableId")

    if rules_id is None:
        print("⚠ No se encontró rulesTableId en systemLayers.")
        return []

    tabla_reglas = FeatureLayer(f"{item.url}/{rules_id}", gis)
    resultado = tabla_reglas.query(where="1=1", out_fields="*", return_all_records=True)

    if diagnostico:
        print(f"\nReglas encontradas: {len(resultado.features)}")

    return [f.attributes for f in resultado.features]


def get_associations(item, gis, diagnostico=False, limite=None):
    """
    Consulta la tabla de asociaciones reales de la Utility Network.
    """
    system_layers = get_system_layers(item, gis)
    assoc_id = system_layers.get("associationsTableId")

    if assoc_id is None:
        print("⚠ No se encontró associationsTableId en systemLayers.")
        return []

    tabla_asociaciones = FeatureLayer(f"{item.url}/{assoc_id}", gis)

    total = tabla_asociaciones.query(where="1=1", return_count_only=True)
    if diagnostico:
        print(f"Total de asociaciones en la red: {total}")

    if limite:
        resultado = tabla_asociaciones.query(where="1=1", out_fields="*", result_record_count=limite)
    else:
        resultado = tabla_asociaciones.query(where="1=1", out_fields="*", return_all_records=True)

    return [f.attributes for f in resultado.features]


def resumen_asociaciones_por_tipo(item, gis):
    """
    Cuenta cuántas asociaciones hay de cada ASSOCIATIONTYPE, sin traer
    los datos completos (solo conteos, liviano incluso con millones de filas).
    """
    system_layers = get_system_layers(item, gis)
    assoc_id = system_layers.get("associationsTableId")

    if assoc_id is None:
        print("⚠ No se encontró associationsTableId en systemLayers.")
        return {}

    tabla = FeatureLayer(f"{item.url}/{assoc_id}", gis)

    # Confirmado con tipos_de_asociacion_presentes(): 1=Container, 2=Structure, 3=Connectivity
    tipos_conocidos = {1: "Container", 2: "Structure", 3: "Connectivity"}

    resumen = {}
    for codigo, nombre in tipos_conocidos.items():
        cantidad = tabla.query(where=f"ASSOCIATIONTYPE={codigo}", return_count_only=True)
        if cantidad > 0:
            resumen[nombre] = cantidad

    return resumen


def tipos_de_asociacion_presentes(item, gis):
    """
    Devuelve los valores distintos de ASSOCIATIONTYPE presentes en la tabla
    de asociaciones, con su conteo, usando agregación en el servidor.
    """
    system_layers = get_system_layers(item, gis)
    assoc_id = system_layers.get("associationsTableId")

    tabla = FeatureLayer(f"{item.url}/{assoc_id}", gis)

    resultado = tabla.query(
        where="1=1",
        out_fields="ASSOCIATIONTYPE",
        group_by_fields_for_statistics="ASSOCIATIONTYPE",
        out_statistics=[{
            "statisticType": "count",
            "onStatisticField": "ASSOCIATIONTYPE",
            "outStatisticFieldName": "conteo"
        }]
    )

    return [f.attributes for f in resultado.features]


def get_layer_fields(item, gis, layer_index, diagnostico=False):
    """
    Consulta la definición de una capa/tabla específica y devuelve sus
    campos con nombre técnico, alias, tipo y dominio (si tiene).

    Returns:
        Una lista de diccionarios, uno por campo:
        [{"nombre": ..., "alias": ..., "tipo": ..., "dominio": {codigo: nombre, ...} o None}]
    """
    url = f"{item.url}/{layer_index}"
    token = gis._con.token

    respuesta = requests.get(url, params={"f": "json", "token": token}, verify=False)
    data = respuesta.json()

    if diagnostico:
        print(f"Respuesta cruda de la capa {layer_index} (recortada):")
        print(json.dumps(data, indent=2)[:2000])

    campos = data.get("fields", [])
    resultado = []

    for campo in campos:
        dominio_info = None
        dominio = campo.get("domain")
        if dominio and "codedValues" in dominio:
            dominio_info = {
                cv["code"]: cv["name"] for cv in dominio["codedValues"]
            }

        resultado.append({
            "nombre": campo.get("name"),
            "alias": campo.get("alias"),
            "tipo": campo.get("type"),
            "dominio": dominio_info,
        })

    return resultado


def get_all_layers_fields(item, gis):
    """
    Recorre TODAS las capas y tablas del servicio y devuelve sus campos.

    Returns:
        Un diccionario {nombre_de_capa: [lista de campos]}.
    """
    resultado = {}

    for capa in item.layers:
        try:
            nombre = capa.properties.name
            idx = capa.properties.id
            resultado[nombre] = get_layer_fields(item, gis, idx)
        except Exception as e:
            print(f"⚠ No se pudo leer campos de capa [{capa.properties.id}]: {e}")

    for tabla in item.tables:
        try:
            nombre = tabla.properties.name
            idx = tabla.properties.id
            resultado[nombre] = get_layer_fields(item, gis, idx)
        except Exception as e:
            print(f"⚠ No se pudo leer campos de tabla [{tabla.properties.id}]: {e}")

    return resultado