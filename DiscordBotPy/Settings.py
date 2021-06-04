import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_LOL = os.environ.get("API_LOL")
API_DISCORD = os.environ.get("API_DISCORD")
