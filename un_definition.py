from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import es_utility_network, get_network_definition, resumen_domain_networks, resumen_asset_groups

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)

if not es_utility_network(item, gis):
    print(">>> NO es una Utility Network. Deteniendo.")
else:
    definicion = get_network_definition(item, gis, diagnostico=False)

    if definicion:
        # --- Domain Networks y Tiers ---
        resumen_dn = resumen_domain_networks(definicion)
        print(f"Domain Networks encontrados: {len(resumen_dn)}\n")
        for dn in resumen_dn:
            tipo = "ESTRUCTURA" if dn["es_estructura"] else "RED"
            print(f"=== {dn['nombre']} ({tipo}) ===")
            print(f"  Tiers: {len(dn['tiers'])}")
            for tier in dn["tiers"]:
                print(f"    - {tier['nombre']} (rank: {tier['rank']})")
        print()

        # --- Asset Groups y Asset Types ---
        resumen_ag = resumen_asset_groups(definicion)
        print("=== ASSET GROUPS Y ASSET TYPES ===\n")
        for dn in resumen_ag:
            print(f"--- Domain Network: {dn['domain_network']} ---")
            for source in dn["sources"]:
                total_tipos = sum(len(ag["asset_types"]) for ag in source["asset_groups"])
                print(f"  Source [{source['tipo']}] layerId={source['layerId']}: "
                      f"{len(source['asset_groups'])} asset groups, {total_tipos} asset types")
                for ag in source["asset_groups"]:
                    print(f"    - {ag['nombre']} (código {ag['codigo']}): {len(ag['asset_types'])} tipos")
            print()