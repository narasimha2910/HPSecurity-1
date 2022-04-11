import cv2
import os

class VideoCapture:
    def __init__(self, video_path):
        self.video_path = video_path

    def extract_frames(self):
        cam = self.load_video(self.video_path)
        imageSize = self.image_size(cam)
        frames = []
        count = 0
        while(True):
            ret, frame = cam.read()
            if ret:
                frames.append(frame)
                count += 1
            else:
                break
        self.close_video(cam)
        return ret, frames, imageSize, count

    def load_video(self, path):
        print('Loading video....')
        cam = cv2.VideoCapture(path)
        return cam

    def close_video(self, cam):
        print('Closing video....')
        cam.release()
        cv2.destroyAllWindows()
    
    def image_size(self, cam):
        width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return height, width


    

