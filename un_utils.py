"""Utilidades reutilizables para trabajar con Utility Networks."""

import json
import requests
from arcgis.features import FeatureLayerCollection


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

    Args:
        definicion: el diccionario devuelto por get_network_definition.

    Returns:
        Una lista de diccionarios, uno por domain network:
        [{
            "domain_network": nombre,
            "sources": [
                {"tipo": "junction"|"edge", "layerId": ..., "sourceId": ...,
                 "asset_groups": [{"nombre": ..., "codigo": ...,
                                    "asset_types": [{"nombre": ..., "codigo": ...}]}]}
            ]
        }]
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