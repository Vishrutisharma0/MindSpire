from flask import Flask
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from mind_spire.routes import pages

load_dotenv()

def create_app():
    app=Flask(__name__)
    client=MongoClient(os.getenv("MONGODB_URI"))
    app.db=client.MindSpire
    app.config["SECRET_KEY"]=os.environ.get("SECRET_KEY")



    app.register_blueprint(pages)
    return app