from flask import Response, json

class JsonResponse(Response):
    default_mimetype = 'application/json'
    def __init__(self, responseData):
        response = json.dumps({
            "data": responseData
        })
        super(JsonResponse, self).__init__(response=response, headers={"Access-Control-Allow-Origin": "*"})
