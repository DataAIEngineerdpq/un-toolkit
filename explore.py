from arcgis.gis import GIS
from getpass import getpass
import config

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

resultados = gis.content.search(query="title:SIGNORMAL", item_type="Feature Service", max_items=10)
print(f"Se encontraron {len(resultados)} feature services:\n")
for item in resultados:
    print("-", item.title, "|", item.type, "|", item.id)