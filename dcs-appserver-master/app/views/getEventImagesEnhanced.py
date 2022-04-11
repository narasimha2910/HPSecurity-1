'''
Purpose: Given an event_type name and incident_id,fetch all images of the incident_id under event_type.
If no incident_id,then supply all images of all incidents under the event_type
'''

from app import app
from flask import request
import os
from decouple import config
from app.reponseClasses.jsonReponse import JsonResponse
import base64

# Here slno === ID


@app.route('/get-events-images')
def getEventImages():

    print(f"****GetEventImages API called*****")

    # grab the event type from the query string
    query_event_name = ''
    if 'event_name' in request.args.keys():
        query_event_name = request.args['event_name']
        print(f"Event_name: {query_event_name}")
    else:
        print(f"Event type is a compulsory paramter for the api")
        return "event_type is a compulsory parameter", 404

    # when we req for an event report,we pass the incident slno as query string in URL
    query_incident_id = None
    if 'event' in request.args.keys():
        query_incident_id = request.args['event']
    print(f"Queried event # is {query_incident_id}")

    # the path of the folder to explore and fetch images from
    start_path = os.path.join(config('PROCESSED_CLIP_DIR'), query_event_name)
    print(f"Start Path {start_path}")

    # dictionary to the store the result
    event_images = {}

    # split every path to roots,dirs & files(non dirs) in "DFS" manner
    for root_dir_path, sub_dirs, files in os.walk(start_path):
        print(f"Curr Folder Path: {root_dir_path}")
        print(f"Sub directories: {sub_dirs}")
        print(f"Files in the curr folder: {files}")

        # remove the lengthy start_path to get relative path wrt to the start_path(here pv/event_name)
        curr_folder_name = root_dir_path.replace(start_path, '')
        print(f"curr_folder_name: {curr_folder_name}")

        # traversed_folder_names[0] - Incident id
        #traversed_folder_names[1] - CAM_IP
        # traversed_folder_names[2] - folder caled "images"
        traversed_folder_names = []
        # Dont add start_dir(ie pv/event_name) to the traversed folders list
        if(curr_folder_name != ''):
            # the initial portion of relative path is "",hence ignore it
            traversed_folder_names = curr_folder_name.split(os.sep)[1:]
        # print(f"Levels:{traversed_folders}")

        # dont traverse videos folder
        #if len(traversed_folder_names) >= 1 and len(traversed_folder_names) <= 3:
        if len(traversed_folder_names) >= 1:

            # at height=1,the folder for diff event slno is traversed
            curr_incident_id = traversed_folder_names[0]
            print(f"Curr Incident id: {curr_incident_id}")

            # brace to store cam_ip and images under it
            if (curr_incident_id not in event_images.keys() and (query_incident_id != None and query_incident_id == curr_incident_id)) or (query_incident_id == None):
                event_images[curr_incident_id] = {}

            # fill only images of the required event slno or else fill in all images
            if (query_incident_id != None and query_incident_id == curr_incident_id) or (query_incident_id == None):
                for file in files:
                    if file.endswith("png") or file.endswith("jpg"):

                        # at height=2 in the dir tree,we have the cam IP address
                        cam_ip = f"cam_{getCamId(traversed_folder_names[1])}"
                        print(f"Cam ip is {cam_ip}")

                        # work with the images
                        with open(os.path.join(root_dir_path, file), "rb") as f:
                            # encode the image in base 64
                            encoded_string = base64.b64encode(f.read())

                            if cam_ip not in event_images[curr_incident_id].keys():
                                event_images[curr_incident_id][cam_ip] = {}

                            event_images[curr_incident_id][cam_ip][file] = encoded_string.decode(
                                'ascii')
                        print(f"**Added File {file} into the return data**")

                        #only one image should be suplied as thumbnail for event report
                        if query_incident_id==None: break

            # if queried only for specific event id,then early return the images for that event id
            print(f"Len of traversal is : {len(traversed_folder_names)}")
            if traversed_folder_names[-1]=='images' and query_incident_id != None and curr_incident_id == query_incident_id:
                print(f"Early return!")
                #print(f"The data returned: {event_images}")
                return JsonResponse(event_images)

    #print(f"Event images: {event_images}")
    return JsonResponse(event_images)


# hash map to assign each cam_ip an cam_id
cam_ips = []


def getCamId(ip):
    if ip not in cam_ips:
        cam_ips.append(ip)
    # account for zero based indexing of list
    return cam_ips.index(ip) + 1


# data to be sent
'''
For a particular event_type:-
{
    "data":{
        "1":{
            "cam_1":{
                "0.jpg":"base_64_encoded"
            }
        }
    }
}

'''
