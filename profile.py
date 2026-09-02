from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import es_utility_network

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)
print("Servicio:", item.title)

if es_utility_network(item, gis):
    print(">>> Es una Utility Network. ✓")
else:
    print(">>> NO es una Utility Network.")