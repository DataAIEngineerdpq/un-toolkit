from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from getpass import getpass
import config

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username, "\n")

item = gis.content.get(config.SIGNORMAL_ID)
print("Servicio:", item.title)
print("URL:", item.url, "\n")

coleccion = FeatureLayerCollection(item.url, gis)
props = coleccion.properties
tiene_un = "controllerDatasetLayers" in props or "utilityNetworkLayerId" in props
print(">>> ¿Es una Utility Network?:", "SÍ" if tiene_un else "NO (feature service común)")