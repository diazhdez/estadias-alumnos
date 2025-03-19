import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv('MONGO_URI',"mongodb+srv://equipo:YCPoxTsZv3Lr6N95@cluster0.kigg6os.mongodb.net/?retryWrites=true&w=majority")
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME')


    