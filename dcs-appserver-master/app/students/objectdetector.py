import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.python.framework.indexed_slices import IndexedSlicesSpec
import tensorflow_hub as hub
import tensorflow as tf
import math

NUMBER_OF_INTERVALS = 5
MIN_SCORE = .1

MODULE_HANDLE = 'https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1'

class ObjectDetector:
    def __init__(self, imageSize):
        self.imageSize = imageSize
        print('Start Loading Model....')
        self.model = hub.load(MODULE_HANDLE)
        self.detector = self.model.signatures['default']
        print('Done Loading Model....')

    def convert_to_tensor(self, frame):
        image = tf.convert_to_tensor(frame, dtype='uint8')
        return image
    
    def display_image(self, image):
        interval = self.imageSize[0] // NUMBER_OF_INTERVALS
        major_ticks = np.arange(0, self.imageSize[0], interval)
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xticks(major_ticks)
        plt.grid(which='major')
        plt.imshow(image)
        plt.show()

    def find_centroid(self, indices, locations):
        centroids = []
        for index in indices:
            ymin, xmin, ymax, xmax = tuple(locations[index])
            centroids.append(((xmin+xmax)/2, (ymin+ymax)/2))
        return centroids
    
    def find_region(self, centroids):
        x = self.imageSize[0] // NUMBER_OF_INTERVALS
        regions = []
        for point in centroids:
            regions.append(math.ceil((point[0]*self.imageSize[0]) / x))
        return regions

    def run_detector(self, frame, item):
        image = self.convert_to_tensor(frame)
        converted_image = tf.image.convert_image_dtype(image, tf.float32)[tf.newaxis, ...]
        result = self.detector(converted_image)
        result = {key: value.numpy() for key, value in result.items()}

        classes = np.array([value.decode('ascii').lower() for value in result['detection_class_entities']])
        boxes = result['detection_boxes']
        scores = result['detection_scores']
        indices = []
        for index in range(len(classes)):
            if classes[index] in item and scores[index] >= MIN_SCORE:
                indices.append(index)
        
        indices = np.array(indices)
        centroids = self.find_centroid(indices, boxes)
        regions = self.find_region(centroids)

        return regions, classes, boxes, indices

        
