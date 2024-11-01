import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

DB_CONFIG = {
    'server': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_DATABASE'),
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
}
