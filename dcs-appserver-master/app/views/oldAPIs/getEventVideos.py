from app import app
from flask import request, Response
import os
import flask
import re
from decouple import config
from app.utils.listDirectoryRecursively import listDirectoryRecursively
from app.reponseClasses.jsonReponse import JsonResponse

processedDir = config('PROCESSED_CLIP_DIR')


@app.route('/get-event-video-sources')
def eventVideoSources():
    eventId = request.args['event'] if "event" in request.args else None
    processedDirTree = listDirectoryRecursively(processedDir)

    '''
    {'1': {'videos': {'files': ['1%17.513.175.44@20200202_201109']}, 'images': {'files': ['0.png']}}, 'files': ['15%17.453.344.94@20200202_201109.mp4.mp4', '1%17.453.344.94@20200202_201109.mp4']}
    '''

    return JsonResponse({
        eventId: list(processedDirTree[eventId].keys(
        )) if eventId in processedDirTree else []
    })


def get_chunk(full_path, byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
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


@app.route('/event-video')
def get_file():
    @flask.after_this_request
    def after_request(response):
        response.headers.add('Accept-Ranges', 'bytes')
        return response

    eventId = request.args['event'] if "event" in request.args else None
    source = request.args['source'] if "source" in request.args else None
    videoPath = os.path.join(processedDir, eventId, source, "videos")
    videoFileName = os.listdir(videoPath)[0]

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(
        os.path.join(videoPath, videoFileName), byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp
