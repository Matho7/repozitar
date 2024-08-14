import os
import base64

# Funkcia na generovanie cookie_secret
def generate_cookie_secret():
    return base64.b64encode(os.urandom(32)).decode('utf-8')

# Parametre pripojenia k databáze
db_host = "your_db_host"  # Zadajte hostiteľa databázy
db_database = "your_db_name"  # Zadajte názov databázy
db_user = "your_db_user"  # Zadajte používateľské meno databázy
db_password = "your_db_password"  # Zadajte heslo do databázy

# OAuth2 nastavenia pre Google
oauth2_client_id = "your_client_id"  # Zadajte váš OAuth2 client ID
oauth2_client_secret = "your_client_secret"  # Zadajte váš OAuth2 client secret
oauth2_redirect_uri = "http://localhost:8080/auth/callback"  # Zadajte redirect URI

# Cookie secret
cookie_secret = generate_cookie_secret()
