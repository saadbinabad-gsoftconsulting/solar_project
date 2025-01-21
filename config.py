import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MONGO_URI = 'mongodb+srv://saad:gsoft2hai@cluster0.ekcwi.mongodb.net/'