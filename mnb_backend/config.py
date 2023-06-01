import os
from dotenv import load_dotenv

# load .env environment variables
load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL_TEST = os.environ['DATABASE_URL_TEST']

# LIMITER_STORAGE_URI = os.environ['LIMITER_STORAGE_URI']
#
# MAX_COUNT = 50
# MIN_COUNT = 1
