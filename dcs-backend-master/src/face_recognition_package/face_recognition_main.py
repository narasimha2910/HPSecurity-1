import os
import shutil
from face_recognition_package import dcs_video_face_detection_edit as dcsf
from helpers import parse_video_file_name
import traceback
from operator import itemgetter
import cv2
from db_utils import dcsDB
import pickle
import numpy as np
import face_recognition

class Analyzer:
    # s_video_dir -> the directory containing the videos that needs to be analysed
    # s_processed_dir -> the dir where the results nees to be stored
    def __init__(self, dcsDB, s_videos_dir, s_processed_dir, backendDir):
        self.dcsDB = dcsDB

        # Surveillance Video Directory
        self.s_videos_dir = s_videos_dir
        self.s_processed_dir = s_processed_dir

        self.processing_flag = True

        #load all known faces
        self.known_faces = None
        self.f=None
        with open(os.path.join(backendDir,"models","trained_models","knownFaceEncs.pkl"),"rb") as self.f:
            self.known_faces=np.array(pickle.load(self.f))

    # Location where known images are kept
    def train(self,knownFacesDir):
        all_face_encs = []
        # Processing Known Images
        print("Processing Known Images...")
        for name in os.listdir(knownFacesDir):
            print("Folder Name :{name}".format(name=name))
            for sample in os.listdir(f"{knownFacesDir}/{name}"):
                print("Image picked :{sample}".format(sample=sample))
                sample_image = face_recognition.load_image_file(
                    f"{knownFacesDir}/{name}/{sample}")
                # print(sample_image)
                # All known images should have a single known face
                sample_encoding = face_recognition.face_encodings(sample_image)[0]
                # add encoding of the face to the list
                all_face_encs.append(sample_encoding)
                    
        pickle.dump(all_face_encs, self.f)
        print(f"Number of encs : {len(all_face_encs)}")

    def exeFaceRec(self,s_video_filename):
        try:
            full_video_file_path = os.path.join(
                self.s_videos_dir, s_video_filename)
            parsed_file_name = parse_video_file_name(s_video_filename)
            
            extension = parsed_file_name["extension"]
            incident_id = parsed_file_name["incident_id"]
            source_ip = parsed_file_name["ip"]
            datetime = parsed_file_name["db_datetime"]
            timestamp = parsed_file_name["timestamp"]

            # {
            #     "unknownCount":0,
            #     "unknownFacesPILimage":[[],[],[],..],
            #     "unknownFacesFrameNumbers":[[],[],[]...]
            # }
            analyze_result = dcsf.predict(full_video_file_path,self.known_faces)

            unknownCount,unknownFacesPILimage,unknownFacesFrameNumbers = itemgetter('unknownCount','unknownFacesPILimage','unknownFacesFrameNumbers')(analyze_result)

            # allImgs = []
            # for aImgSet in unknownFacesPILimage:
            #     for aImg in aImgSet:
            #         allImgs.append(aImg)
            # unknownFacesPILimage = allImgs
            # del allImgs
            unknownFacesPILimage = [aImg for aImgSet in unknownFacesPILimage for aImg in aImgSet]
            unknownFacesFrameNumbers = [aFrameNum for aFrameNumSet in unknownFacesFrameNumbers for aFrameNum in aFrameNumSet]

            print(f"Analysed result:")
            print(f"Filename is: {s_video_filename}")
            print(f"# of unknown Faces: {unknownCount}")
            print(f"# of unknown faces images: {len(unknownFacesPILimage)}")
            print(f"The frame numbers of unknwown faces: {unknownFacesFrameNumbers}")

            # Moving procesed video from input videos directory to processed video directory, and
            # also saving the know person thumbnail if any

            #create the "face_recognition/incident_id" folder in pv dir 
            faceRecRes_dir_path = os.path.join(self.s_processed_dir, 'face_recognition',incident_id)
            os.makedirs(faceRecRes_dir_path, exist_ok=True)

            #create "face_recognitionid/ip" dir
            camera_dir_path = os.path.join(faceRecRes_dir_path, source_ip)
            os.makedirs(camera_dir_path, exist_ok=True)

            #create "face_recognition/id/ip/videos" and "face_recognition/id/ip/images"
            videos_path = os.path.join(camera_dir_path, "videos")
            images_path = os.path.join(camera_dir_path, "images")
            os.makedirs(videos_path, exist_ok=True)
            os.makedirs(images_path, exist_ok=True)

            processed_file_path = os.path.join(
                videos_path, f"{timestamp}.{extension}")

            '''os.popen(
                f"ffmpeg -y -i '{full_video_file_path}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{processed_file_path}.mp4' && rm {full_video_file_path}")
            os.remove(full_video_file_path)
            shutil.move(full_video_file_path, processed_file_path)'''
            
            #copy the video once processing is done
            shutil.copy(full_video_file_path,processed_file_path)

            # print("Press Enter to proceede saving the images and detaisl to db...")
            #input()

            # save the images in the "images" folder
            for i, image_with_person_face in enumerate(unknownFacesPILimage):
                #print(f"Type of img: {type(image_with_person_face[0])}")
                cv2.imwrite(os.path.join(images_path, f"{i}.jpg"),image_with_person_face)

            # saving the processed information to database
            self.dcsDB.insertIncident(1,{'incident_id':incident_id,'datetime': datetime,'source_ip':source_ip, 'unknownCount':unknownCount,'unknownFacesFrameNumbers':unknownFacesFrameNumbers}) ##uncomment

            print("Done saving to DB..")

        except Exception as e:
            print(f"[Exception] in face_rec {e}")
            # print("Press enter to proceede..")
            # input()

            print(e)
            print(traceback.format_exc())
        # print(f"{s_video}: (counts: {analyze_result['counts']}, matches: {analyze_result['matches']}, known: {analyze_result['known'].keys()})")


if __name__ == '__main__':
    print("Connecting to db....")
    db_host = 'localhost'
    pg_user = 'postgres'
    pg_password = 'strong18sep'

    pg_db = 'dcsdb'

    db = dcsDB(db_host, pg_user, pg_password, pg_db)
    db.connect()
    #db.createTables()
    print("Connected to db...")

    print("Starting ML Algo...")
    a = Analyzer(db,'/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/tpv',"/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/pv")
    a.exeFaceRec("7%203.22.191.170@20200202_201109-2021-08-23_16.26.21.mp4")
    print("Done with ML algo...")