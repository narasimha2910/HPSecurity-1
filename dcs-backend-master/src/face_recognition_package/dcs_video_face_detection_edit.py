import os
import pickle
import face_recognition
import cv2
import numpy as np

# globalconstants

# CNN is newer but slower on CPU
MODEL = "hog"
# the higher we go,more matches but less accurate
TOLERANCE = 0.3
#how many frames to skip for faster processing
SKIP=2

# function to add new unknown face or update encodings of known unknown faces
def unknownFaceAdder(theEnc, theFrameNum,theFrameImg, theDict):
	#print("Unknown face fun called")
	#print(f"The dict passed by ref: {theDict}")
	#print(f"Datatype of img: {type(theFrameImg)}")

	isPresent = False
	# if first unknown face
	if len(list(theDict.keys())) == 0:
		#print("First face")
		theDict["unknown0"] = {'encs':[theEnc],'frames':[theFrameNum],'pil':[theFrameImg]}
		#print(f"The val is : {theDict['unknown0']['frames']}")
		return

	# if not,compare the enc of unknwon face and store the encodings along with frame number to prevent repetition
	# if the unknown face already present in the dict
	for k in list(theDict.keys()):
		#print(f"key {k}")
		#print(f"The type of encs is: {type(theDict[k]['encs'])}")
		#print(f"The shape is {np.shape(theDict[k]['encs'])}")
		#print(f"The frames are: {theDict[k]['frames']}")
		tempRes = face_recognition.compare_faces(theDict[k]['encs'], theEnc)
		#print(f"Temp res: {tempRes}")
		if True in tempRes:
			isPresent = True
			# replace with recent enc
			theDict[k]['encs'] = [theEnc]
			#print(f"The dict {theDict}")
			theDict[k]['frames'].append(theFrameNum)
			theDict[k]['pil'].append(theFrameImg)

	# if new unknown face
	if not isPresent:
		theDict[f"unknown{len(theDict.keys())}"] = {'encs':[theEnc],'frames':[theFrameNum],'pil':[theFrameImg]}
		return

# function to give details of unknown faces given a video
def predict(video_location,knownFacesEncodings):
	'''Obj to store unknown faces and their recent encoding
		{
		unknown1:{enc:e2,frameNums:[1,5,7]},
		unknown2:{encs:e3,frameNums:[6,9,2]}
		}'''
	ukFacesFound = {}

	# load the surveillance video
	video = cv2.VideoCapture(video_location)

	'''
	Run through every frame,
	Find all faces
	For each face see which face it matches with from known-faces-images
	If unknown faces found,group them
	'''
	frameNum = 1
	procNum=1

	# # all known face encodings
	# knownFacesEncodings = []
	# with open('knownFaceEncs.pkl','rb') as f:
	# 	knownFacesEncodings = np.array(pickle.load(f))

	# until all frames are read
	# ***skip half the frames and see***
	while True:
		# read a frame
		didFrameRead, frameImg = video.read()
		# if frame was read correclty
		if didFrameRead:
			if frameNum%SKIP == 0:
				# grab locations of all faces in the frame
				allFaceLocs = face_recognition.face_locations(
					frameImg, model=MODEL)
				# grab the encodings of all the faces in the frame
				allFaceEncs = face_recognition.face_encodings(
					frameImg, allFaceLocs)
				#print(f"Number of faces:{len(allFaceEncs)}")

				# for each face found in the frame along with its encodings,compare with the known faces
				for aFaceEnc in allFaceEncs:
					#print("Analysing a face...")
					res = face_recognition.compare_faces(knownFacesEncodings,aFaceEnc)
					#print(f"Res:{res}")

					if True in res:
						#print("Known face")
						pass
					else:
						unknownFaceAdder(aFaceEnc,frameNum,frameImg,ukFacesFound)
				procNum+=1
					
			frameNum += 1
		else:
			# break out of while loop since all frames are read
			break

	video.release()

	print("-------------------Analytics----------------------")
	print("Frames read : {frames}".format(frames=frameNum-1))
	print("Frames processed : {frames}".format(frames=procNum-1))
	print("Number of Unknown faces : {x}".format(x=len(ukFacesFound.keys())))
	print("--------------------------------------------------")

	return {
		'unknownCount':len(ukFacesFound.keys()),
		"unknownFacesPILimage":[ukFacesFound[k]['pil'] for k in list(ukFacesFound.keys())],
		"unknownFacesFrameNumbers":[ukFacesFound[k]['frames'] for k in list(ukFacesFound.keys())]
	}


if __name__ == "__main__":
	print("Running face rec...")
	#train('/home/chandradhar/Projects/HPE/dcs-backend-master/images/known-faces')
	prediction = predict(f'/home/white_wolf/Downloads/ImprovedVersion/dcs-appserver-master/tpv/{input()}.mp4')
	print(f"The prediction {prediction['unknownCount']},{prediction['unknownFacesFrameNumbers']}")

'''for aFaceEnc in allFaceEncs:
				# initially the face is Unknown
				isFaceUK = True
				# go through all the knwon faces in dataset
				for k in knownFacesEncodings:
					print('looking through known faces...')
					#print(f"Enc: {k}")
					# tempRes would be an array of bools telling whether the face matched with any known face encodings
					tempRes = face_recognition.compare_faces(
						[k], aFaceEnc, TOLERANCE)
					# even if one encoding matches
					if True in tempRes:
						print("Mathcing enc?")
						isFaceUK = False
						# early break as we dont care about known faces
						#break
				# if after going through all the known faces and the currFace is still not matched,then unknown face
				if isFaceUK:
					unknownFaceAdder(aFaceEnc, frameNum, ukFacesFound)'''