from flask.helpers import send_from_directory
from app import app
from flask import request, Response
import os
import flask
import re
from decouple import config
from app.utils.listDirectoryRecursively import listDirectoryRecursively
from app.reponseClasses.jsonReponse import JsonResponse

processedDir = config('PROCESSED_CLIP_DIR')

# This API will return only the path name of each video present on the server
@app.route('/get-event-video-sources')
def eventVideoSources():

    # grab the event type from the query string
    query_event_name = ''
    if 'event_name' in request.args.keys():
        query_event_name = request.args['event_name']
        print(f"Event_name: {query_event_name}")
    else:
        print(f"Event type is a compulsory paramter for the api")
        return "event_type is a compulsory parameter", 404

    queryIncidentId = request.args['event'] if "event" in request.args else None
    processedDirTree = listDirectoryRecursively(processedDir)
    print(f"Incident IDs in the event are {processedDirTree[query_event_name].keys()}")
    '''
    The tree structure: {'unusual': {}, 'dummy-tailgating': {'1': {'videos': {'files': ['1%17.513.175.44@20200202_201109']}, 'images': {'files': ['0.png']}}, 'files': ['15%17.453.344.94@20200202_201109.mp4.mp4', '1%17.453.344.94@20200202_201109.mp4']}, 'unknown': {'1': {'15.213.155.94': {'videos': {'files': ['1580674269.mp4.mp4']}, 'images': {'files': ['1.jpg', '0.jpg']}}}}}

    '''

    # we need to return the relative video path of a particular event_id of the given event_type
    vidSources = {queryIncidentId: []}

    incidentIdChk=queryIncidentId in list(processedDirTree[query_event_name].keys())
    print(f"Incident ID check {incidentIdChk}")

    camIps=list(processedDirTree[query_event_name][queryIncidentId].keys())
    print(f"cam ips {camIps}")

    for camip in camIps:
        vidFlderChk="videos" in list(processedDirTree[query_event_name][queryIncidentId][camip].keys())
        print(f"Video folder check {vidFlderChk}")

        filesInVidFldrChk="files" in list(processedDirTree[query_event_name][queryIncidentId][camip]["videos"].keys())
        print(f"Checking if there are valid files in the video directory inside {[camip]} dir: {filesInVidFldrChk}")

        if incidentIdChk and vidFlderChk and filesInVidFldrChk:
            print("Video files present on server!")
            allImgs=processedDirTree[query_event_name][queryIncidentId][camip]["videos"]["files"]
            for imgName in allImgs:
                vidSources[queryIncidentId].append(f"{camip}/"+imgName)

    print(f"Video sources are {vidSources}")
    '''
    Returned data example:
    {'1': ['1%17.513.175.44@20200202_201109']} 
    '''
    return JsonResponse(vidSources)

    #http://localhost:5000/event-video?event=7&source=49_53_56_48_54_55_52_50_54_57_46_109_112_52&event_name=face_recognition


def get_chunk(full_path, byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    print(f"File size {file_size}")
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size

# This API is responsible for returning the video given by the relative path name of the video .


@app.route('/event-video')
def get_file():
    @flask.after_this_request
    def after_request(response):
        response.headers.add('Accept-Ranges', 'bytes')
        return response

    # grab the event_id
    queryEventId = None
    if "event" in request.args:
        queryEventId = request.args['event']
    else:
        return "This API needs eventID", 404

    # grab the event type from the query string
    query_event_name = ''
    if 'event_name' in request.args.keys():
        query_event_name = request.args['event_name']
        print(f"Event_name: {query_event_name}")
    else:
        print(f"Event type is a compulsory paramter for the api")
        return "event_type is a compulsory parameter", 404

    queryVidFilename = None
    queryVidFilename = request.args["source"]
    if queryVidFilename == None:
        return "video filename is a compulsory parameter", 404
    
    #The client sends the name of the video file in ascii and dash format and the server needs to decrypt it.
    #Eg:49_37_49_55_46_53_49_51_46_49_55_53_46_52_52_64_50_48_50_48_48_50_48_50_95_50_48_49_49_48_57
    
    j = '' #video file name
    k = '' #camera ip folder
    splitted = queryVidFilename.split("_")

    #process till '/'
    for counter,i in enumerate(splitted):
        if int(i)!=47: #ascii value of '/' is 47
            k+=chr(int(i))
        else:
            break

    for l in range(counter+1,len(splitted)): #get video name after '/'
        j += chr(int(splitted[l]))

    queryIp=k
    queryVidFilename = j
    print(f"***Vid file name {queryVidFilename}")
    print(f"Reletive location {k}/{j}")

    # videoFullPath = os.path.join(
    #     processedDir, query_event_name, queryEventId,queryIp, "videos", queryVidFilename)
    # print(f"****The full path of the video is {videoFullPath}****")

    # range_header = request.headers.get('Range', None)
    # byte1, byte2 = 0, None
    # if range_header:
    #     match = re.search(r'(\d+)-(\d*)', range_header)
    #     groups = match.groups()

    #     if groups[0]:
    #         byte1 = int(groups[0])
    #     if groups[1]:
    #         byte2 = int(groups[1])

    # chunk, start, length, file_size = get_chunk(videoFullPath, byte1, byte2)
    # if chunk : print("***Chunk present***")
    # resp = Response(chunk, 206, mimetype='video/mp4',
    #                 content_type='video/mp4', direct_passthrough=True)
    # resp.headers.add(
    #     'Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    # return resp

    return send_from_directory(os.path.join(processedDir,query_event_name,queryEventId,queryIp,"videos"),queryVidFilename)
