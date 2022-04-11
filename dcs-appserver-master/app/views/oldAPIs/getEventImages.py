from app import app
from flask import request, json
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

    # when we have an event report,we pass the event slno as query string in URL
    query_event_slno = None
    if 'event' in request.args.keys():
        query_event_slno = request.args['event']
    print(f"Queried event # is {query_event_slno}")

    # the path to explore and fetch images from
    start_path = os.path.join(config('PROCESSED_CLIP_DIR'), query_event_name)
    print(f"Start Path {start_path}")

    # dictionary to the store the result
    event_images = {}

    # split every path to roots,dirs & files(non dirs) in DFS manner
    for root_dir_path, sub_dirs, files in os.walk(start_path):
        print(f"Curr Folder Path: {root_dir_path}")
        print(f"Sub directories: {sub_dirs}")
        print(f"Files in the curr folder: {files}")

        # remove the lengthy start_path to get relative path wrt to the start_path(here pv/event_name)
        curr_folder_name = root_dir_path.replace(start_path, '')
        print(f"curr_folder_name: {curr_folder_name}")

        # traversed_folder_names[0] - Event Slno
        #traversed_folder_names[1] - CAM_IP
        # traversed_folder_names[2] - folder caled "images"
        traversed_folder_names = []
        # Dont add start_dir(ie pv/event_name) to the traversed folders list
        if(curr_folder_name != ''):
            # the initial portion of relative path is "",hence ignore it
            traversed_folder_names = curr_folder_name.split(os.sep)[1:]
        # print(f"Levels:{traversed_folders}")

        # dont traverse videos folder
        if len(traversed_folder_names) >= 1 and len(traversed_folder_names) <= 3:

            # at height=1,the folder for diff event slno is traversed
            curr_event_slno = traversed_folder_names[0]
            print(f"Curr Event SLNO: {curr_event_slno}")

            # brace to store cam_ip and images under it
            if curr_event_slno not in event_images.keys() and ((query_event_slno != None and query_event_slno == curr_event_slno) or (query_event_slno == None)):
                event_images[curr_event_slno] = {}

            # fill only images of the required event slno or else fill in all images
            if (query_event_slno != None and query_event_slno == curr_event_slno) or (query_event_slno == None):
                for file in files:
                    if file.endswith("png") or file.endswith("jpg"):

                        # at height=2 in the dir tree,we have the cam IP address
                        cam_ip = f"cam_{getCamId(traversed_folder_names[1])}"

                        # work with the images
                        with open(os.path.join(root_dir_path, file), "rb") as f:
                            # encode the image in base 64
                            encoded_string = base64.b64encode(f.read())

                            if cam_ip not in event_images[curr_event_slno].keys():
                                event_images[curr_event_slno][cam_ip] = {}

                            event_images[curr_event_slno][cam_ip][file] = encoded_string.decode(
                                'ascii')
                        print(f"**Added File {file} into the return data**")

            # if queried only for specific event id,then early return the images for that event id
            print(f"Len of traversal is : {len(traversed_folder_names)}")
            if len(traversed_folder_names) == 3 and query_event_slno != None and curr_event_slno == query_event_slno:
                print(f"Early return!")
                print(
                    f"The data returned: {event_images}")
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


# sample data to be sent when no event slno is provided :- Assumption that there is no "event type" scheme available
'''
{
    "data": {
        "1": {
            "cam_1": {
                "0.jpg": "",
                "1.jpg": ""
            }
        },
        "2": {
            "cam_1": {
                "0.jpg": ""
            }
        },
        "3": {
            "cam_1": {
                "0.jpg": ""
            }
        },
        "4": {
            "cam_1": {
                "0.jpg": ""
            }
        }
    }
}

'''

# data to be sent :- Assumption that there is "event type" scheme available
'''
if <tailgating>
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
