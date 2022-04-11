from .objectdetector import ObjectDetector
from .videocapture import VideoCapture
from .facedetection import FaceDetection
import os
def predictor():
    VIDEO_FILE_PATH = '/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/found'
    IMAGESIZE = (290.0, 290.0)
    videos = os.listdir('/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/found')
    print(videos)

    info_json = []
    object_detector = ObjectDetector(imageSize=IMAGESIZE)
    face_detector = FaceDetection()

    for video_id in videos:
        path = f'{VIDEO_FILE_PATH}/{video_id}'
        new_predictions=[]
        new_regions=[]
        info_dict={}
        info_dict["video_link"]=video_id
        video_capture = VideoCapture(path)
        ret, frames, imageSize, count = video_capture.extract_frames()

        for frame_no in range(len(frames)):
            regions, classes, boxes, indices = object_detector.run_detector(frames[frame_no], [ 'human face'])
            #print(regions)
            face_boxes = []
            for index in indices:
                if classes[index] == 'human face':
                    (bottom, left, top, right) = boxes[index]
                    face_boxes.append((top, right, bottom, left))
            predictions = face_detector.predict_faces(frames[frame_no], face_boxes)
            for item in predictions:
                #print(item)
                if item != "Unknown" and item is not None and item not in new_predictions  :
                    new_predictions.append(item)
                    if regions not in new_regions:
                        new_regions.append(regions)
            if new_predictions:
                info_dict["face_status"]=new_predictions
                info_dict["person_found_at"]=new_regions
            else :
                regions, classes, boxes, indices = object_detector.run_detector(frames[frame_no], [ 'man'])
                if regions:
                    info_dict["face_status"]=["Unknown"]
                    if regions not in new_regions:
                        new_regions.append(regions)
                    info_dict["person_found_at"]=new_regions
        info_json.append(info_dict)       
    print(info_json)           
    return info_json
        
