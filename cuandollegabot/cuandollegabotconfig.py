import os

DB_FULL_URI = os.environ.get('MONGODB_URI')
DB_CLIENT = os.environ.get('DB_CLIENT')
TOKEN = os.environ.get('TOKEN')
OWNER_ID = os.environ.get('OWNER_ID')
SKIP_PARADA = os.environ.get('SKIP_PARADA', False)
