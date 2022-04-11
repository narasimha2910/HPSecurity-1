import pickle
import cv2
from PIL import Image, ImageDraw
import face_recognition
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
import numpy as np
import dlib
import os

# constants
MODELS_DIR = os.path.join(os.path.dirname(__file__), f"..{os.sep}", "models")
DEBUG_MODE = False
KNOWN_FACE_DISTANCE_THRESHOLD = 0.45
FACE_DETECTION_MODEL_PATH = os.path.join(MODELS_DIR, "trained_knn_model_new.clf")
MOBILENET_SSD_PROTOTEXT_PATH = os.path.join(MODELS_DIR, f"mobilenet_ssd{os.sep}MobileNetSSD_deploy.prototxt")
MOBILENET_SSD_MODEL_PATH = os.path.join(MODELS_DIR, f"mobilenet_ssd{os.sep}MobileNetSSD_deploy.caffemodel")
OBJECT_DETECTION_SKIP_FRAMES = 6
OBJECT_DETECTION_CONFIDENCE_THRESHOLD = 0.4

def decode_faces(frame, classifier):
    to_return = []
    frame_face_locations = face_recognition.face_locations(frame)

    if len(frame_face_locations) > 0:
        # since cv2 reads in BGR, we convert it to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(rgb_frame)

        draw = ImageDraw.Draw(pil_image)

        for (top, right, bottom, left) in frame_face_locations:
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        face_encodings = face_recognition.face_encodings(frame, known_face_locations=frame_face_locations)

        closest_distances = classifier.kneighbors(face_encodings, n_neighbors=1)

        encoding_predictions = classifier.predict(face_encodings)
        for i, (distances, name, (top, right, bottom, left)) in enumerate(zip(closest_distances[0], encoding_predictions, frame_face_locations)):
            # for each face locations
            # get the best distance
            min_distance = distances[0]

            if(min_distance <= KNOWN_FACE_DISTANCE_THRESHOLD):
                draw.text((left, bottom), f"{name} [{round(min_distance, 2)}]", fill=(255, 255, 0), align="left")

            cX = int((left + right) / 2.0)
            cY = int((bottom + top) / 2.0)
            location_centroid = (cX, cY)

            to_return.append({
                "location_centroid": location_centroid,
                "name": name,
                "distance": min_distance,
                "image": pil_image
            })

        del draw

    return to_return

def analyze(video_file_path):
    print("[INFO] loading models...")
    # loading objection detection model
    object_detection_net = cv2.dnn.readNetFromCaffe(MOBILENET_SSD_PROTOTEXT_PATH, MOBILENET_SSD_MODEL_PATH)

    # loading face-detection model
    knn_classifier = None
    with open(FACE_DETECTION_MODEL_PATH, "rb") as f:
        knn_classifier = pickle.load(f)

    print("[INFO] loading video file...")
    # load the surveillance video from the provided path
    video = cv2.VideoCapture(video_file_path)

    # frame dimensions initialization (it will be set as soon as we read the first frame from the video)
    W = None
    H = None

    # instantiate the centroid tracker, then initialize a list to store
    # each of the dlib correlation trackers, followed by a dictionary to
    # map each unique object ID to a TrackableObject
    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    trackers = []
    trackableObjects = {}

    # initialize the total number of frames processed thus far
    totalFrames = 0

    while True:
        # grab the next frame
        ret, frame = video.read()
        # if while viewing a video, we did not grab a frame then we
        # have reached the end of the video
        if not ret:
            break

        # convert the frame from BGR to RGB for dlib
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # if the frame dimensions are empty, set them
        if W is None or H is None:
            (H, W) = frame.shape[:2]

        # initialize the list of bounding box rectangles returned by either (1) the object detector or
        # (2) the correlation trackers
        rects = []

        if totalFrames % OBJECT_DETECTION_SKIP_FRAMES == 0:
            trackers = []

            blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
            object_detection_net.setInput(blob)
            detections = object_detection_net.forward()

            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > OBJECT_DETECTION_CONFIDENCE_THRESHOLD:
                    idx = int(detections[0, 0, i, 1])
                    if idx != 15: # 15 is the index for the person object in the model being used
                        continue
                    box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                    (startX, startY, endX, endY) = box.astype("int")

                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(startX, startY, endX, endY)
                    tracker.start_track(rgb, rect)

                    trackers.append(tracker)
        else:
            for tracker in trackers:
                tracker.update(rgb)
                pos = tracker.get_position()

                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())

                rects.append((startX, startY, endX, endY))

        objects = ct.update(rects)

        faces = decode_faces(frame, knn_classifier)

        if (DEBUG_MODE == True and  len(faces)> 0):
            print("faces detected", len(faces), list(map(lambda x: x["name"], faces)))

        for (objectID, tracked_object) in objects.items():
            centroid = tracked_object["centroid"]
            (startX, startY, endX, endY) = tracked_object["rect"]



            to = trackableObjects.get(objectID, None)
            if to is None:
                to = TrackableObject(objectID, centroid)

            for face in faces:
                (face_centroid_x, face_centroid_y) = face["location_centroid"]
                if (face_centroid_x >= startX and face_centroid_x <= endX and face_centroid_y >= startY and face_centroid_y <= endY):
                    to.faceData.append(face)

                    if(DEBUG_MODE == True):
                        cv2.putText(frame, face["name"], (face_centroid_x - 10, face_centroid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.circle(frame, (face_centroid_x, face_centroid_y), 4, (0, 255, 0), -1)

            if (DEBUG_MODE == True):
                frame = cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)

            trackableObjects[objectID] = to

        if(DEBUG_MODE == True):
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # increment the total number of frames processed thus far and
        # then update the FPS counter
        totalFrames += 1


    print(trackableObjects)

    res = {
        "personCount": 0,
        "knownCount": 0,
        "knowPeople": [],
        "knownFacesPILimage": [],
        "unknownFacesPILimage": []
    }
    for persondata in trackableObjects.values():
        res["personCount"] += 1
        # find the best face for the person
        faces_sorted_by_distance = sorted(persondata.faceData, key=lambda k: k["distance"])
        if(len(faces_sorted_by_distance) > 0):
            best_face = faces_sorted_by_distance[0]
            if(best_face["distance"] <= KNOWN_FACE_DISTANCE_THRESHOLD):
                # The best match is whitin the threshold, so the person is considered to  be known person
                res["knownCount"] += 1
                res["knowPeople"].append(best_face["name"])
                res["knownFacesPILimage"].append(best_face["image"])
            else:
                # The best match for identified faces for the person is not below the threshold, so the person is considered to be unknown
                res["unknownFacesPILimage"].append(best_face["image"])

    video.release()

    if (DEBUG_MODE == True):
        # close any open windows
        cv2.destroyAllWindows()

    return res

if __name__ == "__main__":
    file_path = f"../toProcess/15.213.215.205@20200116_195658.avi"
    DEBUG_MODE = True
    analysis = analyze(file_path)
    print(analysis)
