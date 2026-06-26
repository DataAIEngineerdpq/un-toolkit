from arcgis.gis import GIS
from getpass import getpass

# Datos de conexión (NO son secretos, pueden vivir en el código)
portal_url = "https://el_portal"
usuario = "user"

# La contraseña se pide en el momento y nunca se guarda
gis = GIS(portal_url, usuario, getpass("Contraseña del Portal: "))

# Confirmación de que la conexión funcionó
print("Conectado como:", gis.users.me.username)
print("Rol:", gis.users.me.role)