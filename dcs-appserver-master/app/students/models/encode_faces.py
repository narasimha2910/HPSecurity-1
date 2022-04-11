from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

DATASET_PATH = '/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/known-faces'
ENCODING_PATH ='/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/models/newencodings.pickle'
DETECTION_METHOD = 'cnn' # cnn or hog  

imagePaths = list(paths.list_images(DATASET_PATH))
knownEncodings = []
knownNames = []

for (i, imagePath) in enumerate(imagePaths):
    print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))


    name = imagePath.split(os.path.sep)[-2]
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model=DETECTION_METHOD)
    encodings = face_recognition.face_encodings(rgb, boxes)
    
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

data = {"encodings": knownEncodings, "names": knownNames}
f = open(ENCODING_PATH, "wb")
f.write(pickle.dumps(data))
f.close()