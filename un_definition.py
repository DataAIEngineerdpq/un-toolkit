from arcgis.gis import GIS
from getpass import getpass
import config
from un_utils import (
    es_utility_network,
    resumen_domain_networks,
    resumen_asset_groups,
    get_associations,
    resumen_asociaciones_por_tipo,
    tipos_de_asociacion_presentes,
)

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)

if not es_utility_network(item, gis):
    print(">>> NO es una Utility Network. Deteniendo.")
else:
    print(">>> Es una Utility Network. ✓\n")

    # --- Asociaciones: muestra pequeña ---
    print("=== Muestra de asociaciones (5) ===")
    muestra = get_associations(item, gis, limite=5)
    for a in muestra:
        print(a)

    # --- Asociaciones: resumen con el diccionario de tipos conocidos (incompleto) ---
    print("\n=== Asociaciones por tipo (diccionario conocido) ===")
    resumen_tipos = resumen_asociaciones_por_tipo(item, gis)
    for tipo, cantidad in resumen_tipos.items():
        print(f"  {tipo}: {cantidad:,} asociaciones")

    # --- Asociaciones: TODOS los valores reales de ASSOCIATIONTYPE (para corregir el diccionario) ---
    print("\n=== Valores reales de ASSOCIATIONTYPE (agregación en servidor) ===")
    for fila in tipos_de_asociacion_presentes(item, gis):
        print(fila)