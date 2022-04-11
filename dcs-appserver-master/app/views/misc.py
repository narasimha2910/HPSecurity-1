from app import app
import os
import base64
from app.reponseClasses.jsonReponse import JsonResponse

@app.route('/get-logo')
def logo():
    path_to_logo = os.path.join(os.getcwd(),"app","assets", "HPE_logo.svg")
    print("***************")
    print(path_to_logo)
    print("***********")
    with open(path_to_logo, "rb") as logoImage:
        encoded_string = base64.b64encode(logoImage.read())
        return JsonResponse(encoded_string.decode('ascii'))
