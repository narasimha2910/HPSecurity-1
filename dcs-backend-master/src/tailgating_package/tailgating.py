from collections import OrderedDict as odict
from posixpath import join
import numpy as np
from scipy.spatial.distance import cdist
import numpy as np
import cv2
import os
from pathlib import Path
from helpers import createVidImgFolders, parse_video_file_name
from helpers import fpsFinder
from db_utils import dcsDB

# constants
RED = (0, 0, 255)
GREEN = (0, 255, 0)
ACTIVE = True

# confidence threshold
CONF = 0.5
SCALEFAC = 0.007843
THRESHOLD=0.4

class TailgateAnalyser():
    def __init__(self, tpv_dir, pv_dir, root_dir,backend_dir, dcsDb, entryExitIps,isTiny=False,num_thumbnails=4):

        # load model and its prototext
        yolo_files_dir = os.path.join(backend_dir,"models","yolo_models")

        if not isTiny:
            self.yolo = cv2.dnn.readNet(os.path.join(yolo_files_dir,"yolov3.weights"), os.path.join(yolo_files_dir,"yolov3.cfg"))
        else:
            self.yolo = cv2.dnn.readNet(os.path.join(yolo_files_dir,"yolov3-tiny.weights"), os.path.join(yolo_files_dir,"yolov3-tiny.cfg"))

        #read the classes on which the model was trained
        with open(os.path.join(yolo_files_dir,"coco.names"), "r") as file:
            self.classes = [line.strip() for line in file.readlines()]

        #model layers
        layer_names = self.yolo.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.yolo.getUnconnectedOutLayers()]

        # vid processing related
        self.processing_flag = True
        self.tpv_dir = tpv_dir
        self.pv_dir = pv_dir
        self.root_dir = root_dir
        self.num_thumbnails = num_thumbnails

        # db related
        self.dcsDb = dcsDb
        self.entryExitIps = entryExitIps

        # curr video details
        self.incident_id = None
        self.source_ip = None
        self.db_dateime = None

    # helper functions

    def assignColor(self, tailgateOID):
        if tailgateOID[0] != None:
            return RED
        return GREEN

    # function to update DB with needed info
    def dbUpdater(self):
        print(f"Updating the DB....")
        try:
            self.dcsDb.insertIncident(2,{'incident_id':self.incident_id,'datetime': self.db_datetime,'source_ip':self.source_ip}) ##uncomment
            print("Done saving to DB..")
        except Exception as e:
            print(f"[Exception] unable to save to db due to the exception {e}")
        return

    def exeTailgating(self,vid_filename):

        # create the directory for tailgating if it doesnt already exist in the pv folder
        # print(f"[INFO] Creating tailgating dir")
        # Path(os.path.join(self.pv_dir, "tailgating")).mkdir(
        #     parents=True, exist_ok=True)

        print(f"Videos available: {vid_filename}")

        # details about video
        parsed_file_name = parse_video_file_name(
            vid_filename)

        #print(f"parsed file name: {parsed_file_name}")

        self.extension = parsed_file_name["extension"]
        #print(f"Extension: {extension}")

        self.incident_id = parsed_file_name["incident_id"]
        #print(f"Incident ID: {self.incident_id}")

        self.source_ip = parsed_file_name["ip"]
        #print(f"IP: {self.source_ip}")

        self.db_datetime = parsed_file_name["db_datetime"]
        self.timestamp = parsed_file_name["timestamp"]
        #print(f"Timestamp: {timestamp}")

        #only certain ip cam vids allowed
        if self.source_ip in self.entryExitIps:
            try:
                # green color indicates no tailgating
                isTailgateFrame = (0, 255, 0)
                # putting this variable as an list so that its passed by ref
                tailgateOID = [None]

                vid_path = os.path.join(self.tpv_dir, vid_filename)
                print(f"Vid path: {vid_path}")

                # frame dimensions
                (H, W) = (None, None)

                # create the folder for the specific incident id and ip inside it
                # Path(os.path.join(self.pv_dir, "tailgating", f"{incident_id}", f"{source_ip}")).mkdir(
                #     parents=True, exist_ok=True)

                # create folder for videos
                # vid_folder=os.path.join(self.root_dir, self.pv_dir, "tailgating", f"{self.incident_id}", f"{self.source_ip}", "videos")
                # Path(vid_folder).mkdir(parents=True, exist_ok=True)

                # # and for images
                # img_folder=os.path.join(self.root_dir, self.pv_dir, "tailgating", f"{self.incident_id}", f"{self.source_ip}", "images")
                # Path(img_folder).mkdir(parents=True, exist_ok=True)

                vid_folder,img_folder=createVidImgFolders("tailgating",self.root_dir,self.pv_dir,self.incident_id,self.source_ip)
                print(f"The vid and img folder in pv is at : {vid_folder},{img_folder}")

                # load the video
                vs = cv2.VideoCapture(vid_path)

                fps=fpsFinder(vs)
                print(f"Vid Running @ fps {fps}")

                # creating centroid tracker OBJECT
                ct = CentroidTracker(vs, tailgateOID, self.dbUpdater)

                # start saving the video
                frame_width = int(vs.get(3))
                frame_height = int(vs.get(4))
                size = (frame_width, frame_height)
                print(f"Frame size:{size}")

                #to save image thubmnails
                save_img_count=0

                # settings related to saving the video
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                processed_vid_path = os.path.join(vid_folder, f"{self.timestamp}.{self.extension}")
                out = cv2.VideoWriter(processed_vid_path, fourcc, 10, size)
                print(processed_vid_path) 
                #input()
                print(f"Metadata processed for saving video")
                
                # counter for storing images of tailgating event
                prevStoredImgOID = None

                # start processing frames of the given video
                doRead = True
                while doRead:
                    # read frame from videofps
                    doRead, frame = vs.read()

                    if doRead:
                        # update the counter
                        if len(ct.counters) > 0:
                            for counter in ct.counters:
                                if counter.state == ACTIVE:
                                    counter.update()

                        """ # for stopping video
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            doread = False
                            break """

                        # set the frame size to the intial frame size
                        if W == None or H == None:
                            # print(frame.shape)
                            (H, W) = frame.shape[0:2]
                        #print("W,H is {x},{y}".format(x=W,y=H))

                        # create blob(ie pre-processed image) from the frame
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

                        for output in outputs: #for each layer output
                            for detection in output: #for each detection
                                #print("Processing a detected box....")
                                scores = detection[5:] #detection[0:4] is the dim of the box,remaining give the prob of the object detected being of a particular class

                                class_id = np.argmax(scores) #index of the class with max probability

                                confidence = scores[class_id] #get the confidence val for the class detected with max probability

                                if confidence > CONF:
                                    #store the max probability to object i accross various detections in various frames
                                    #print(f"Detected class {self.classes[class_id]}")

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

                        box_indxs = cv2.dnn.NMSBoxes(det_details["boxes"],det_details["confidences"],CONF,THRESHOLD)
                        rects = []

                        if len(box_indxs):
                            for box_indx in box_indxs.flatten():
                                #print(f"Type(box_indx) {type(box_indx)}")
                                #get the strong box
                                (x,y,w,h )= det_details['boxes'][box_indx]
                                rects.append((x,y,x+w,y+h))

                        # send the detected objects to Centroid Tracker
                        trackedObjs = ct.loop(rects)

                        isTailgateFrame = self.assignColor(tailgateOID)

                        # trackedObjs is a dict containging OBJ ID and OBJ Centroid,draw them
                        for (oID, cent) in trackedObjs.items():
                            if isTailgateFrame == RED:
                                alert = "TAILGATING"
                                cv2.putText(
                                    frame, alert, (cent[0], cent[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 4)

                                # store one frame of each tailgating object
                                if prevStoredImgOID == None or (prevStoredImgOID != None and prevStoredImgOID < oID):
                                    prevStoredImgOID = oID

                                    #save this image
                                    if save_img_count < self.num_thumbnails and save_img_count%fps==0:
                                        cv2.imwrite(os.path.join(img_folder,f"{save_img_count}.jpg"),frame)
                                        save_img_count+=1

                            txt = "ID {x}".format(x=oID)
                            # put near centroid
                            cv2.putText(frame, txt, (cent[0]-10, cent[1]-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED if isTailgateFrame == RED else GREEN, 2)
                            
                            # draw circle for centroid
                            cv2.circle(frame, (cent[0], cent[1]), 4, RED if isTailgateFrame == RED else GREEN, -1)

                        # cv2.imshow("Frame", frame)
                        # write frame to output
                        print("Writing frame",frame)
                        out.write(frame)
                        # cv2.imshow("Results",frame)

                    else:
                        break

                out.release()

                #update db
                self.dbUpdater()
                
                print("[INFO] Saved the video!")
                vs.release()
                # print("[INFO] Released the video stream!")
                cv2.destroyAllWindows()
                # print("[INFO] Destroyed all the Windows!")

                # delete the file once done processing
                #os.remove(vid_path)

            except Exception as e:
                print(e)

                
# class to create Person Objects that represent the Person we are tracking


class Person():
    def __init__(self, objID, lim, func1):
        self.id = objID
        self.elapsedFrames = 0
        self.makeNone = func1
        self.lim = lim
        self.state = ACTIVE

    def isTimeOut(self):
        if self.elapsedFrames >= self.lim:
            return True
        else:
            return False

    def update(self):
        self.elapsedFrames += 1
        # if timer runs out for this instance of Person class
        if self.isTimeOut():
            self.makeNone()
            self.state = not ACTIVE

# Object Tracking Algorithm


class CentroidTracker():
    def __init__(self, videoStream, tailgateOID, dbUpdater, maxDissapeared=5, maxDistance=130,tailgateTime=15):
        self.nextObjID = 0
        # obj id - centroid mapping
        self.detectedObjs = odict()
        # object id - lost frames mapping
        self.dissapearedObjs = odict()
        # the max num of consecutive frames the object has to be lost to remove it
        self.maxDisappearedFrames = maxDissapeared
        # euclidian distance threshold to consider them as same centroids
        self.maxEucDistance = maxDistance
        # initialize the curr obj scanning
        self.currObjID = None
        # fps of video
        self.fps=fpsFinder(videoStream)
        # time interval after which the currObj should be made None
        # if fps of video is 9,then after 15 seconds or 9*15=135 frames,the timer should beep
        self.noneFrame = self.fps*tailgateTime
        # boolean to start the timer for the first object
        self.isFirstObject = True
        # array to store all detected objects
        self.counters = []
        # tailgate tracker
        self.tailgateOID = tailgateOID
        # the number of frames an detected object can miss future detection
        maxDissapeared=self.fps//2

    
    def makeNone(self):
        print("Made None")
        self.currObjID = None

    def setCurrObjID(self, newID):
        self.currObjID = newID

    def remObj(self, objID):
        # remove from detected object list
        if objID in list(self.detectedObjs.keys()):
            del self.detectedObjs[objID]

        # remove from dissapreared obj list
        if objID in list(self.dissapearedObjs.keys()):
            del self.dissapearedObjs[objID]

        # if its the tailgate object,then remove it
        if objID == self.tailgateOID[0]:
            self.tailgateOID[0] = None

    def tailGateCheck(self):
        currObjIDs = list(self.detectedObjs.keys())
        # print("CurrObjID : {x}".format(x=self.currObjID))
        # print("Len of detectedObjects : {x}".format(x=len(currObjIDs)))

        # if the currObj is None and first object is detected
        if len(currObjIDs) == 1 and self.currObjID == None:
            return False
        # if the currObj is the only object in the frame,then no tailgaiting
        if len(currObjIDs) == 1 and currObjIDs[0] == self.currObjID:
            return False
        # if there is only one object in the frame and if its not the currObj,then tailgaiting
        if len(currObjIDs) == 1 and currObjIDs[0] != self.currObjID:
            return True
        # if there are more than 1 objects in the frame,then tailgating
        if len(currObjIDs) > 1:
            return True
        # case when no objects in the frame ie len(currObjIDs == 0)
        return False

    def addObj(self, toAddCentroid):
        # use the next available object ID to store the object
        self.detectedObjs[self.nextObjID] = toAddCentroid
        self.dissapearedObjs[self.nextObjID] = 0
        self.nextObjID += 1

        # check for tailgaiting only when adding new item

        # when we are adding a new object && there is no tailgaiting happening.
        # (if already objects exists,then it will not enter inside the below stmnt)
        if not self.tailGateCheck():
            # check if its the first object to get tracked
            if self.isFirstObject:
                self.isFirstObject = False
                # call timeout to make currObjectID to None after self.noneTime interval
                # in a seperate thread
                self.setCurrObjID(self.nextObjID-1)
                print("The currObj using door is {x}".format(x=self.currObjID))

            # if its not first object and if currObjID = None and since we have an object added to the frame,timeout on it to make it None after 15s
            elif not self.isFirstObject and self.currObjID == None:
                self.setCurrObjID(self.nextObjID-1)
                # call the timeout function

            print("Starting Timer for object {x} for {y} frames".format(
                x=self.currObjID, y=self.noneFrame))
            # start counter
            self.counters.append(
                Person(self.currObjID, self.noneFrame, self.makeNone))
        else:
            print("####TAILGAIT####")
            self.tailgateOID[0] = [self.nextObjID-1]
            print("TAILGATED : {x}".format(x=self.tailgateOID[0]))

    # centroid calculator given [x1,y1,x2,y2]
    def centroidCalculator(self, a_coord):
        # x,y coordinate per list,hence shape 2
        centroid = np.zeros(2)
        # print("Len of centroid output array would be {x}".format(x = len(centroid)))
        # print("Len of input is {X}".format(X=len(a_coord)))
        centroid[0] = int((a_coord[0]+a_coord[2])/2.0)
        centroid[1] = int((a_coord[1]+a_coord[3])/2.0)
        return centroid

    # recieves a list of coordinates of all detected object
    # coords is a list of [startX,startY,endX,endY] - bounding box around the object
    def loop(self, coords):
        # print("Input Coordinates : {x}".format(x=coords))
        # print("Len of input array {x}".format(x=len(coords)))

        # if no objects detected,all objs have been lost for the curr frame
        if len(coords) == 0:
            # print("Zero coords list length")
            # for each object:
            for objID in list(self.dissapearedObjs.keys()):
                self.dissapearedObjs[objID] += 1

                # check if num of frames each obj has been lost is equal to the maxDissapeared param
                if self.dissapearedObjs[objID] >= self.maxDisappearedFrames:
                    # Stop tracking
                    self.remObj(objID)

            return self.detectedObjs

        # if objs detected, then:

        # print("Non Zero length of coords")
        # store centroid for each of the input box,hence x and y coord for each input box
        cent_arr_shape = (len(coords), 2)
        centroids = np.zeros(cent_arr_shape, dtype="int")

        # calc the centroid for the box and store it in the np array
        for i, _ in enumerate(coords):
            centroids[i] = self.centroidCalculator(coords[i])
        # print("Centroid {x}".format(x=centroids))

        # if no object stored/detected till now,store each of them
        if len(self.detectedObjs) == 0:
            # print("No object,Adding one!")
            for a_cent in centroids:
                # key - objID and val - centroid
                self.addObj(a_cent)
        else:
            # else,we are tracking some objects:
            # hence find the distance between the each object's centroid and the
            # input boxes centroid
            # already tracking  object IDs list
            objIDs = list(self.detectedObjs.keys())
            # already tracking object Centroids list
            objCentroids = list(self.detectedObjs.values())

            # numpy array of centroids of each object
            # print("The Centroids of existing objs are {x}".format(x=objCentroids))
            allObjCentroids = np.zeros((len(objCentroids), 2))
            for i, ob in enumerate(objCentroids):
                # print("ob {x}".format(x=ob))
                allObjCentroids[i] = ob
            # print("The shape of allObjCentroids is {x}".format(x=allObjCentroids.shape))

            # calc the dist between all detected objects centroids and input boxes centroids
            pairDist = cdist(allObjCentroids, centroids)
            # print("Distance Array {x}".format(x=pairDist))
            # the shape would be (# object centroids, # input boxes)
            # print("Shape of Dist array {x}".format(x=pairDist.shape))
            # pair_dist rows - registered object's centroid
            # pair_dist columns - centroid of input boxes
            # each entry is distance from curr centroid to one of the inpt centroid

            # hence,find min element along each row and sort the list of min elemts,return the
            # index of the sorted array
            rows = pairDist.min(axis=1).argsort()

            # pairDist matrix contains array of rows.
            # find the index of the min element in each row considering the rows in the order
            # given by [rows]
            cols = pairDist.argmin(axis=1)[rows]

            # now we have the row numbers of the min elements along each row and the index of the
            # min elements of each row in their particular row lists of the 2D matrix
            # print("The rows and cols are : {x}".format(x=list(zip(rows,cols))))

            # set to store the used rows and cols
            consideredObjs = set()
            consideredBoxes = set()

            # zip(row,col) gives the smallest tuple - which is row and col number of the pairDist matrix entry with min distance
            for row_col in zip(rows, cols):
                if row_col[0] in consideredObjs or row_col[1] in consideredBoxes:
                    # either the row or col is already considered,then skip this
                    continue

                # if the distance between the two centroids is greater than max distance for association,then they are not same objects.
                if pairDist[row_col[0], row_col[1]] > self.maxEucDistance:
                    print(f"Dist of sep : {pairDist[row_col[0], row_col[1]]}")
                    continue

                # otherwise grab the object id of the min dist pair and update the centroid
                # distance and reset the disappeared frame
                self.detectedObjs[objIDs[row_col[0]]] = centroids[row_col[1]]
                self.dissapearedObjs[objIDs[row_col[0]]] = 0

                # add it to the considered obj and cols set
                consideredObjs.add(row_col[0])
                consideredBoxes.add(row_col[1])

            # there still might be Objects which might not have been included in the used rows set
            # hence they could be objects potentially lost/disappeared
            # range(0,D.shape[0]) - gives all row numbers
            temp = set(range(0, pairDist.shape[0]))
            # find the row numbers not used
            unusedObjs = temp.difference(consideredObjs)

            # there still might be input box coordinates not included
            # range(0,D.shape[1]) - gives all col numbers
            temp = set(range(0, pairDist.shape[1]))
            unusedBoxes = temp.difference(
                consideredBoxes)  # find the col # not used

            # now considering the case where the number of object centroid is more than input
            # centroid .This means that some objects have disappeared
            if pairDist.shape[0] >= pairDist.shape[1]:
                for a_row in unusedObjs:
                    self.dissapearedObjs[objIDs[a_row]] += 1

                    # check to see if max frames of dissapearance has been caused
                    # if so then de register it
                    if self.dissapearedObjs[objIDs[a_row]] > self.maxDisappearedFrames:
                        self.remObj(self.dissapearedObjs[objIDs[a_row]])

            else:
                # more number of centroids than existing num of obj centroids
                # hence register the objects
                for a_col in unusedBoxes:
                    self.addObj(centroids[a_col])
        # print("Detected Objects : {x}".format(x=self.detectedObjs))
        return self.detectedObjs


if __name__ == "__main__":

    db_host = 'localhost'
    pg_user = 'postgres'
    pg_password = 'chandra69chandra'

    pg_db = 'dcsdb'

    db = dcsDB(db_host, pg_user, pg_password, pg_db)
    db.connect() ##uncomment

    t = TailgateAnalyser(
    '/home/chandradhar/Projects/HPE/dcs-appserver-master/tpv',
    "/home/chandradhar/Projects/HPE/dcs-appserver-master/pv",
    '/home/chandradhar/Projects/HPE/dcs-appserver-master', db,
    db.fetchEntryExitIps(),True)   

    t.exeTailgating("15%203.22.191.170@20200202_201109-2021-08-23_16.26.21.mp4")
