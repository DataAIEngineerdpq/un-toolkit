"""Utilidades reutilizables para trabajar con Utility Networks."""

from arcgis.features import FeatureLayerCollection


def es_utility_network(item, gis, diagnostico=False):
    """
    Determina si un item de Feature Service contiene una Utility Network real.

    Args:
        item: el Item del Portal a verificar.
        gis: la conexión GIS activa.
        diagnostico: si es True, imprime las claves del servicio (para depurar).

    Returns:
        True si el servicio contiene una Utility Network, False si no.
    """
    coleccion = FeatureLayerCollection(item.url, gis)
    props = coleccion.properties

    if diagnostico:
        print("Claves disponibles en este servicio:")
        print(list(props.keys()))

    return "controllerDatasetLayers" in props or "utilityNetworkLayerId" in props