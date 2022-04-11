import face_recognition
import pickle

THRESHOLD = .45
ENCODING_PATH = '/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/models/newencodings.pickles'

class FaceDetection:
    def __init__(self):
        self.data = self.load_model()

    def load_model(self):
        # with open(ENCODING_PATH, 'rb') as file:
        #     data = pickle.load(file).read()
        data = pickle.loads(open('/home/white_wolf/Desktop/ImprovedVersion/dcs-appserver-master/app/students/models/newencodings.pickle', 'rb').read())
        return data

    def predict_faces(self, frame, boxes):
        faces_encodings = face_recognition.face_encodings(frame, known_face_locations=boxes)
        names = []
        for encoding in faces_encodings:
            matches = face_recognition.compare_faces(self.data['encodings'], encoding)
            name = 'Unknown'
            if True in matches:
                matchedIndex = [i for (i, value) in enumerate(matches) if value]
                counts = {}
                for i in matchedIndex:
                    name = self.data['names'][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)
        return names

    

    

    