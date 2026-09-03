from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import es_utility_network, get_connectivity_rules

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)

if not es_utility_network(item, gis):
    print(">>> NO es una Utility Network. Deteniendo.")
else:
    reglas = get_connectivity_rules(item, gis, diagnostico=True)

    print(f"\nTotal de reglas: {len(reglas)}\n")
    for regla in reglas[:10]:  # solo las primeras 10 para no saturar la pantalla
        print(regla)