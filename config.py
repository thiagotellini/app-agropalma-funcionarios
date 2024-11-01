# app/config.py

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configurações de conexão com o SQL Server
DB_CONFIG = {
    'server': 'limv19',
    'database': 'HCM',
    'username': 'logUsuControladoria',
    'password': '1l2o3g4U5suControlad5o4r3i2a1',
}
