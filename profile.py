from arcgis.gis import GIS
from getpass import getpass

portal_url = "https://sigcorpqas.eegsa.net/portal"   # tu URL de Portal real
usuario = "utility"

gis = GIS(portal_url, usuario, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

# Traer el item SIGNORMAL por su id
item = gis.content.get("0a979f60f97e407f8fb12d6f26dcc5df")
print("Servicio:", item.title)
print("URL:", item.url, "\n")

# LA PRUEBA: ¿tiene el componente de Utility Network?
flc = item.layers  # primero vemos si el servicio responde
if item.url:
    from arcgis.features import FeatureLayerCollection
    coleccion = FeatureLayerCollection(item.url, gis)
    props = coleccion.properties
    # El controllerDatasetLayers / utilityNetworkLayerId delata una UN
    tiene_un = "controllerDatasetLayers" in props or "utilityNetworkLayerId" in props
    print(">>> ¿Es una Utility Network?:", "SÍ" if tiene_un else "NO (feature service común)")
    print("\nCapacidades del servicio:", props.get("capabilities", "—"))