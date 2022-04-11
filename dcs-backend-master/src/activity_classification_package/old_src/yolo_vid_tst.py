import cv2
import numpy as np
import sys
import os
sys.path.append("/home/chandradhar/Projects/HPE/dcs-backend-master/src")
from helpers import totalFramesFinder
import json

class VideObjectRecognition:
    def __init__(self,isTiny=False):
        if not isTiny:
            self.yolo = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        else:
            self.yolo = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")

        self.classes = []
        self.CONF = 0.3
        self.THRESHOLD=0.4
        self.THICKNESS=2
        self.RED = (255,0,0)

        #read the classes on which the model was trained
        with open("coco.names", "r") as file:
            self.classes = [line.strip() for line in file.readlines()]
        #print(f"Classes {self.classes}")

        #model layers
        layer_names = self.yolo.getLayerNames()
        self.output_layers = [layer_names[i[0] - 1] for i in self.yolo.getUnconnectedOutLayers()]

        #read the activities json
        with open(os.path.join("/home/chandradhar/Projects/HPE/dcs-backend-master/src/activity_detection","activity.json")) as jsonfile:
            self.activities = json.load(jsonfile)

    def video_object_detector(self,vid_name):
        #print(F"Red color is {self.RED,type(self.RED)}")
        #print(f"Classes {self.classes}")

        didRead=True
        (W,H)=(None,None)
        out = None #output video file
        stream = cv2.VideoCapture(vid_name)
        num_classes = len(self.classes)

        ## use numpy arrays to speedup ##
        total_prob = [0]*num_classes #total probability of detetction of obj i across n frames
        num_frames=0
        total_frames= totalFramesFinder(vid_name)
        #print(f"Number of frames={total_frames}")
        #threshold = (totol_frames//2)*self.CONF
        #print(f"Threshold {threshold}")
        #print(f"Total number of frames {total_frames}")

        while didRead:
            didRead,frame = stream.read()
            #print(f"Read frame or not? {didRead}")

            if didRead:
                num_frames+=1
                sys.stdout.write(f"\rCompleted {(num_frames/total_frames)*100}%")
                sys.stdout.flush()
                if W is None or H is None:
                    H,W = frame.shape[:2]
                    #print(f"Vid frame dim {W,H}")
                    #input()

                # remove noise from image
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

                # process the blob
                self.yolo.setInput(blob)
                outputs = self.yolo.forward(self.output_layers)

                # detection details of every frame
                det_details={
                    'class_ids': [],
                    'confidences' : [],
                    'boxes' : []
                }
                #print(f"Det details: \n {det_details}")

                for output in outputs: #for each layer output
                    for detection in output: #for each detection
                        #print("Processing a detected box....")
                        scores = detection[5:] #detection[0:4] is the dim of the box,remaining give the prob of the object detected being of a particular class

                        class_id = np.argmax(scores) #index of the class with max probability

                        confidence = scores[class_id] #get the confidence val for the class detected with max probability
                        # if confidence>0:
                        #     print(f"[TEST] score {confidence}")
                        #     input()

                        if confidence > self.CONF:
                            #store the max probability to object i accross various detections in various frames
                            ##print(f"\n Detected class {self.classes[class_id]} with conf {confidence}\n")
                            
                            #increase the totoal probability
                            #print(f"Inc prob of {self.classes[class_id]}")
                            total_prob[class_id] = total_prob[class_id]+confidence
                                
                            #scale bounding box coordinates back to relative size of the image
                            center_x = int(detection[0]*W)
                            center_y = int(detection[1]*H)

                            box_w = int(detection[2]*W)
                            box_h = int(detection[3]*H)

                            #convert to opencv scale of top left corner of box
                            x = int(center_x - (box_w/2))
                            y = int(center_y - (box_h/2))

                            det_details["boxes"].append((x, y, box_w, box_h))

                            det_details["confidences"].append(float(confidence))

                            det_details["class_ids"].append(class_id)

                #supress the weak boxes and store the indexes of only strong boxes
                #print(det_details)
                box_indxs = cv2.dnn.NMSBoxes(det_details["boxes"],det_details["confidences"],self.CONF,self.THRESHOLD)

                #loop over every box if atleast one box exists
                #print(f"Number of strongly detected boxes {len(box_indxs)}")
                if len(box_indxs):
                    for box_indx in box_indxs.flatten():
                        #print(f"Type(box_indx) {type(box_indx)}")
                        #get the strong box
                        box=det_details['boxes'][box_indx]

                        #extract its top left coordinates and its width,height
                        (x,y,w,h)=box
                        #print(F"The box dim {(x,y,w,h)}")

                        #draw on the frame the box
                        cv2.rectangle(frame,(x,y),(x+w,y+h),self.RED,self.THICKNESS)

                        #write the confidence
                        label=self.classes[det_details["class_ids"][box_indx]]
                        #print(f"Label {label}")

                        conf = det_details["confidences"][box_indx]
                        txt= f"{label}:{conf}"
                        cv2.putText(frame,txt,(x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.RED, 2)

                #save frame
                if out is None:
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    out = cv2.VideoWriter("output.avi", fourcc, 30,(W,H))
                out.write(frame)

                del det_details #delete the details of the frame saved
            else: break
        
        #store the all objects detected
        #use these objects to get the activity
        det_obj_ids = []
        det_objs=[]
        #total_prob.sort()

        for id in range(len(total_prob)):
            prob = total_prob[id]
            if prob != 0:
                det_obj_ids.append(id)
        #print(f"\n Objs:\n")
        id=-1
        for id in det_obj_ids:
            #print(self.classes[id])
            det_objs.append(self.classes[id])

        #print(f"Argmax {self.classes[np.argmax(np.array(total_prob))]}")
        #print(f"Total prob {total_prob}")

        # longest object list match
        det_objs=set(det_objs)
        #print(f"\nDetected Objs are {det_objs}")
        result_activity={"name":None,"common_objs_count":0,"common_objs_percent":0}

        for activity,objs in self.activities.items():
            common_items_num=len(set(objs).intersection(det_objs))
            common_items_perc =common_items_num/len(objs)
            #print(f"Percentage {common_items_perc*100}%")

            if common_items_num>=result_activity["common_objs_count"] and common_items_perc>result_activity["common_objs_percent"]:
                print(f"Activity name {activity}")
                result_activity["common_objs_count"]=common_items_num
                result_activity["name"]=activity
                result_activity["common_objs_percent"]=common_items_perc

        #print(result_activity)
        print("\n[RESULT] The activity is {x}\n".format(x=result_activity["name"]))

        #print("[Announce] saving the video..")
        out.release()
        stream.release()
        cv2.destroyAllWindows()
        #print("[DONE]")



if __name__ == "__main__":
    vor = VideObjectRecognition(True)
    vor.video_object_detector("news_report.mp4")