import argparse
import os
from face_recognition.face_recognition_cli import image_files_in_folder
import face_recognition
import math
from sklearn import neighbors
import pickle

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--traindata", required=True,
                help="path to folder where known person images are kept")
ap.add_argument("-o", "--output", required=True,
                help="path where the trained model will be saved")
ap.add_argument("-v", "--verbose", type=str,
                help="Verbose display to stdout")
args = vars(ap.parse_args())

KNN_ALGORITHM = "ball_tree"

# PARAMS
# train_data_dir <REQUIRED>: Path to folder where known person images are kept. The directory structure must be as follows:-
#
#     <train_dir>/
#         ├── <person1>/
#         │   ├── <somename1>.jpeg
#         │   ├── <somename2>.jpeg
#         │   ├── ...
#         ├── <person2>/
#         │   ├── <somename1>.jpeg
#         │   └── <somename2>.jpeg
#         └── ...
#
# path_to_save_model <REQUIRED>: The path where the trained model for predicting known faces will be saved
# verbose: default False

def face_trainer(train_data_dir, path_to_save_model, verbose=False):
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
                print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))

            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(known_person_images_dir)

    # Determine how many neighbors to use for weighting in the KNN classifier
    n_neighbors = int(round(math.sqrt(len(X))))
    if verbose:
        print("Chosen n_neighbors:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=KNN_ALGORITHM, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if path_to_save_model is not None:
        if(verbose == True):
            print("Saving Model...")
        with open(path_to_save_model, 'wb') as f:
            pickle.dump(knn_clf, f)
            if (verbose == True):
                print("Model Saved!")

    return knn_clf


if __name__ == "__main__":
    trainer_dir_path = args["traindata"] or "C:/Users/dagav/Desktop/office/DCS/SharedPics/Train_Known_Persons"
    path_to_save_model = args["output"] or "C:/Users/dagav/nwsp/personal workspace/dcs-backend/models/trained_knn_model_new.clf"
    verbosity = args["verbose"] or True

    analysis = face_trainer(trainer_dir_path, path_to_save_model, verbose=verbosity)
    print(analysis)
