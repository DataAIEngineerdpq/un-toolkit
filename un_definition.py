from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import es_utility_network, get_network_definition, resumen_domain_networks

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)

if not es_utility_network(item, gis):
    print(">>> NO es una Utility Network. Deteniendo.")
else:
    definicion = get_network_definition(item, gis, diagnostico=False)

    if definicion:
        resumen = resumen_domain_networks(definicion)
        print(f"Domain Networks encontrados: {len(resumen)}\n")

        for dn in resumen:
            tipo = "ESTRUCTURA" if dn["es_estructura"] else "RED"
            print(f"=== {dn['nombre']} ({tipo}) ===")
            print(f"  Tiers: {len(dn['tiers'])}")
            for tier in dn["tiers"]:
                print(f"    - {tier['nombre']} (rank: {tier['rank']})")
            print()