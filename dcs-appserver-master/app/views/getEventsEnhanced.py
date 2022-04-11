'''
Purpose:Get the details of all the events of a particular event type ie access the particular event tpe table from db and fetch all incident details
'''

from app import app
from decouple import config
from app.utils.dbHandler import DbHandler
from app.reponseClasses.jsonReponse import JsonResponse
from flask import request

@app.route('/get-events')
def getEvents():

    print(f"****Called the get-events api*****")
    # grab the event type name
    query_event_name = ''
    if 'event_name' in request.args.keys():
        query_event_name = request.args['event_name']
        print(f"Event_name: {query_event_name}")
    else:
        print(f"Event type is a compulsory paramter for the api")
        return "event_type is a compulsory parameter", 404

    db = DbHandler(config)
    db.connectToDB()

    # fetch all incidents from the database for the particular event type
    incidents = db.getEvents(query_event_name)

    db.disconnectFromDb()
    return JsonResponse(incidents)
