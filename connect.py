from arcgis.gis import GIS
from getpass import getpass
import config

gis = GIS(config.PORTAL_URL, config.USUARIO, getpass("Contraseña del Portal: "))
print("Conectado como:", gis.users.me.username)
print("Rol:", gis.users.me.role)