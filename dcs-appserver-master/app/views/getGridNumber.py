from app import app
from flask import jsonify
from ..students.main import predictor
from decouple import config
from app.utils.dbHandler import DbHandler
from flask_cors import cross_origin

@app.route("/get-grid")
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def get():
    # Here you need to call the function to predict the results
    # return the info_json
    # info_json = Call() Try making info json a list of dictionaries
    # Locations should be in the range 1 to 5
    result = []
    info_json=predictor()
    # info_json = [{
    #     "video_link": "15.213.155.98@20200119_200305.avi",
    #     "person_found_at": [[5, 3]],
    #     "face_status": ["Unknown", "Test"]
    #     },
    #     {
    #     "video_link": "15.213.155.96@20200119_200305.avi",
    #     "person_found_at": [[3, 1]],
    #     "face_status": ["Nandha", "Shashank"]
    #     }]
    for info in info_json:
        res_list = {}
        ip = info["video_link"]
        k = len(ip)
        k = k - 20
        ip = ip[0:k]
        db = DbHandler(config)
        db.connectToDB()
        obj = db.getRack(ip)
        db.disconnectFromDb()
        print(obj)
        rack_initials = obj["rack_from"][0:2]
        rack_start = int(obj["rack_from"][2:])
        locations = []
        for lis in info["person_found_at"]:
            for value in lis:
                found = value - 1
                loc = rack_start + found%5 
                loc = str(loc)
                if len(loc) == 1:
                    loc = "00"+loc
                elif len(loc) == 2:
                    loc = "0"+loc
                locations.append(rack_initials+loc)
                # found = info["person_found_at"] - 1
            # loc = rack_start + found%5 
            # loc = str(loc)
            # if len(loc) == 1:
            #     loc = "00"+loc
            # elif len(loc) == 2:
            #     loc = "0"+loc
        res_list["video_link"] = info["video_link"]
        res_list["person_found_in_rack"] = locations
        res_list["face"] = info["face_status"]
        res_list["location"] = obj["location"]
        result.append(res_list)
    return jsonify(result)