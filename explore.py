from arcgis.gis import GIS
from getpass import getpass

portal_url = "https://sigcorpqas.eegsa.net/portal"   # tu URL real (la que ya funcionó)
usuario = "utility"                                # tu usuario real

gis = GIS(portal_url, usuario, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

# Buscar contenido: pedimos servicios de tipo "Feature Service"
#resultados = gis.content.search(query="", item_type="Feature Service", max_items=50)
resultados = gis.content.search(query="title:SIGNORMAL", item_type="Feature Service", max_items=10)
print(f"Se encontraron {len(resultados)} feature services:\n")
for item in resultados:
    print("-", item.title, "|", item.type, "|", item.id)