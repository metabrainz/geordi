from flask import Flask
from geordi.frontend import frontend

app = Flask(__name__)

app.register_blueprint(frontend)
