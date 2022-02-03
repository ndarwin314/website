from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
bootstrap = Bootstrap(app)
api = Api(app)


from app import routes
