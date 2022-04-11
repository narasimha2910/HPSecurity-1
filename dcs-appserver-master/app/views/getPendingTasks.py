from app import app
import os
from decouple import config
from app.reponseClasses.jsonReponse import JsonResponse

@app.route('/get-pending-events')
def pending():
    count=0
    for file in os.listdir(config['TO_PROCESS_CLIP_DIR']):
        if file.endswith(".mp4") or file.endswith(".avi"):
            count+=1
    return JsonResponse({"remaining":count})