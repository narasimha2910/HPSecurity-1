from app import app
from decouple import config
from app.utils.dbHandler import DbHandler
from app.reponseClasses.jsonReponse import JsonResponse


@app.route('/get-events')
def getEvents():
    db = DbHandler(config)
    db.connectToDB()
    # fetch all incidents from the database
    incidents = db.getEvents()
    db.disconnectFromDb()
    return JsonResponse(incidents)
