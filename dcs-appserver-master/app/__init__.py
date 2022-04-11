from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

from app.views import getEventsEnhanced
from app.views import getEventImagesEnhanced
from app.views import getEventVideosEnhanced
from app.views import getGridNumber
from app.views import misc

