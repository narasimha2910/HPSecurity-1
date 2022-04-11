import re
import moment
import cv2
from pathlib import Path
import os

#create the folders to store processed video and images
def createVidImgFolders(activity_name,root_dir,pv_dir,incident_id,source_ip):
    vid_folder=os.path.join(root_dir, pv_dir, f"{activity_name}" , f"{incident_id}", f"{source_ip}", "videos")
    Path(vid_folder).mkdir(parents=True, exist_ok=True)

    # and for images
    img_folder=os.path.join(root_dir, pv_dir, f"{activity_name}" , f"{incident_id}", f"{source_ip}", "images")
    Path(img_folder).mkdir(parents=True, exist_ok=True)

    #return the locations
    return (vid_folder,img_folder)

#totoal number of frames in  avideo finder
def totalFramesFinder(vid_name):
    didRead=True
    num_frames=0
    stream = cv2.VideoCapture(vid_name)

    while didRead:
        didRead,_=stream.read()

        if didRead: num_frames+=1
        else: break

    stream.release()
    return num_frames

#frames per secon finder
def fpsFinder(vid_stream):
    fps = vid_stream.get(cv2.CAP_PROP_FPS)
    print(
        "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    return fps

#regex to parse file name
def parse_video_file_name(filename):
    # sample expected file name format: 111.111.111.111@20200116_195929-minor.avi
    try:
        regx_filename = r"((.*)%(.*)@([0-9]{8}_[0-9]{6}).*)\.(.*)"
        (filename, incident_id, ip, datetime, file_extension) = re.search(regx_filename, filename).groups()
        timestamp_m = moment.date(f"{datetime}", "YYYYMMDD_HHmmss")
        return {
            "file_name": filename,
            "incident_id": incident_id,
            "ip": ip,
            "db_datetime": timestamp_m.format("YYYY-MM-DD HH:mm:ss"),
            "timestamp": timestamp_m.epoch(),
            "extension": file_extension
        }
    except:
        return None


if __name__ == "__main__":
    res = parse_video_file_name(input())
    print(res)
