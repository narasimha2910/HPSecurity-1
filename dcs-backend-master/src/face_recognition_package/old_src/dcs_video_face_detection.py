import math
from sklearn import neighbors
import os
import os.path
import pickle
import face_recognition
from PIL import Image, ImageDraw
from face_recognition.face_recognition_cli import image_files_in_folder
import cv2

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def train(train_data_dir, path_to_save_model=None, n_neighbors=None, KNN_ALGORITHM='ball_tree', verbose=False):
    X = []
    y = []

    # Loop through each person in the training set
    for known_person_images_dir in os.listdir(train_data_dir):
        if not os.path.isdir(os.path.join(train_data_dir, known_person_images_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_data_dir, known_person_images_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(known_person_images_dir)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=KNN_ALGORITHM, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if path_to_save_model is not None:
        with open(path_to_save_model, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.45):

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # load the surveillance video
    video = cv2.VideoCapture(X_img_path)
    while True:
        ret, frame = video.read()
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        print(f"reading frame, {ret}")
        if not ret:
            print("ret false beaking")
            break

        X_face_locations = face_recognition.face_locations(frame)
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if len(X_face_locations) > 0:

            draw = ImageDraw.Draw(pil_image)

            for (top, right, bottom, left) in X_face_locations:
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            del draw


            faces_encodings = face_recognition.face_encodings(frame, known_face_locations=X_face_locations)

            closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
            # print(closest_distances)
            are_matches = []
            for i in range(len(X_face_locations)):
                dis = closest_distances[0][i][0]
                print(dis)
                are_matches.append(dis <= distance_threshold)

            # are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

            ppp = [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in
                   zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]
            for name, (top, right, bottom, left) in ppp:
                print("- Found {} at ({}, {})".format(name, left, top))
                pil_image.show()




    video.release()
    return []

if __name__ == "__main__":
    full_file_path = "15.213.215.205@20200116_195928.avi"

    predictions = predict(full_file_path, model_path="trained_knn_model.clf")

    for name, (top, right, bottom, left) in predictions:
        print("- Found {} at ({}, {})".format(name, left, top))
