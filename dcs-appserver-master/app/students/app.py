# from flask import Flask, jsonify, request
# from flask_restful import Api, Resource
# from db import db
# from datetime import datetime
# # Import the predict function
# from main import predictor
# app = Flask(__name__)
# api = Api(app)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:strong18sep@localhost:5432/hpe"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# @app.before_first_request
# def create_tables():
#     db.create_all()

# class TestLocations(db.Model):
#     __tablename__ = "test_locations"

#     id = db.Column(db.Integer, primary_key=True)
#     ip_address = db.Column(db.String(255))
#     model = db.Column(db.String(255))
#     location = db.Column(db.String(255))
#     rack_from = db.Column(db.String(255))
#     rack_to = db.Column(db.String(255))
#     created_dt = db.Column(db.DateTime, default=datetime.now())
#     updated_dt = db.Column(db.DateTime)

# class Insert(Resource):
#     def post(self):
#         data = request.get_json()
#         time = datetime.now()
#         ip = data["ip"]
#         model = data["model"]
#         loc = data["loc"]
#         r_from = data["rf"]
#         r_to = data["rto"]
#         test = TestLocations(ip_address=ip, model=model, location=loc, rack_from=r_from, rack_to=r_to, updated_dt=time)
#         db.session.add(test)
#         db.session.commit()
#         return jsonify(data)

# class Train(Resource):
#     def get(self):
#         # Here you need to call the function to predict the results
#         # return the info_json
#         # info_json = Call() Try making info json a list of dictionaries
#         # Locations should be in the range 1 to 5
#         result = []
#         info_json=predictor()
#         # info_json = [{
#         #     "video_link": "15.213.155.98@20200119_200305.avi",
#         #     "person_found_at": [[5, 3]],
#         #     "face_status": ["Unknown", "Test"]
#         #     },
#         #     {
#         #     "video_link": "15.213.155.96@20200119_200305.avi",
#         #     "person_found_at": [[3, 1]],
#         #     "face_status": ["Nandha", "Shashank"]
#         #     }]
#         for info in info_json:
#             res_list = {}
#             ip = info["video_link"]
#             k = len(ip)
#             k = k - 20
#             ip = ip[0:k]
#             obj = TestLocations.query.filter(TestLocations.ip_address == ip).first()
#             rack_initials = obj.rack_from[0:2]
#             rack_start = int(obj.rack_from[2:])
#             locations = []
#             for lis in info["person_found_at"]:
                
#                 for value in lis:
#                     found = value - 1
#                     loc = rack_start + found%5 
#                     loc = str(loc)
#                     if len(loc) == 1:
#                         loc = "00"+loc
#                     elif len(loc) == 2:
#                         loc = "0"+loc
#                     locations.append(rack_initials+loc)
#                     # found = info["person_found_at"] - 1
#                 # loc = rack_start + found%5 
#                 # loc = str(loc)
#                 # if len(loc) == 1:
#                 #     loc = "00"+loc
#                 # elif len(loc) == 2:
#                 #     loc = "0"+loc
#             res_list["video_link"] = info["video_link"]
#             res_list["person_found_in_rack"] = locations
#             res_list["face"] = info["face_status"]
#             res_list["location"] = obj.location
#             result.append(res_list)

#         return jsonify(result)


# api.add_resource(Insert, '/insertInto')
# api.add_resource(Train, '/train')


# if __name__ == "__main__":
#     db.init_app(app)
#     app.run()
