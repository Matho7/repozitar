import os
import base64


# Funkcia na generovanie cookie_secret
def generate_cookie_secret():
    return base64.b64encode(os.urandom(32)).decode('utf-8')


# Parametre pripojenia k databáze
db_host = "147.175.106.248"
db_database = "DB_luptak"
db_user = "xluptak"
db_password = "mArTiN."

# OAuth2 nastavenia pre Google
oauth2_client_id = '964088640320-fttbnu9iucl33bb0p2g1ukmq2p5flehf.apps.googleusercontent.com'
oauth2_client_secret = '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'
oauth2_redirect_uri = 'http://localhost:8080/auth/callback'  # Opravený redirect URI

# Cookie secret
cookie_secret = generate_cookie_secret()
