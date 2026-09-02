from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import es_utility_network

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)
print("Servicio:", item.title)

if not es_utility_network(item, gis):
    print(">>> NO es una Utility Network. Deteniendo.")
else:
    print(">>> Es una Utility Network. ✓\n")

    capas = item.layers
    tablas = item.tables

    print(f"Capas: {len(capas)}")
    print(f"Tablas: {len(tablas)}\n")

    print("=== CAPAS ===")
    for capa in capas:
        nombre = capa.properties.name
        id_capa = capa.properties.id
        print(f"- [{id_capa}] {nombre}", end="")
        try:
            cantidad = capa.query(return_count_only=True)
            print(f": {cantidad} registros")
        except Exception as e:
            print(f": ⚠ no se pudo consultar ({e})")

    print("\n=== TABLAS ===")
    for tabla in tablas:
        nombre = tabla.properties.name
        id_tabla = tabla.properties.id
        print(f"- [{id_tabla}] {nombre}", end="")
        try:
            cantidad = tabla.query(return_count_only=True)
            print(f": {cantidad} registros")
        except Exception as e:
            print(f": ⚠ no se pudo consultar ({e})")