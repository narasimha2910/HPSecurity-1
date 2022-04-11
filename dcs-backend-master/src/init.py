import os
from db_utils import dcsDB
from tailgating_package import tailgating as tail
import multiprocessing as mp
import queue as qu
from face_recognition_package import face_recognition_main as fm
from activity_classification_package import activity_classification as aca
from decouple import config

db = dcsDB(config('dbHost'), config('pgUser'), config('pgPassword'), config('pgDb'))
db.connect()
db.createTables()

doProcessing=True
tpv=config('toProcessDir')
pv=config('processedDir')
appServerDir=config('appServerDir')
backendDir=config('backendDir')
isTiny=True
# Only videos comming from the entry camera should be sent to Tailgating analysis
# For rest of the videos,do Activity recognition and Unknown face recognition parallely

f = fm.Analyzer(db,tpv,pv,backendDir)
t = tail.TailgateAnalyser(tpv,pv,appServerDir, backendDir, db,db.fetchEntryExitIps(),isTiny)
a = aca.activityClassificationAnalyser(tpv,pv,appServerDir, backendDir ,db,db.fetchEntryExitIps(),isTiny)

processes=qu.Queue()
num_jobs=0

while doProcessing:
    #loop through all videos present
    for jid,s_video_filename in enumerate(os.listdir(tpv)):
        #convert the functons to processes
        task1 = mp.Process(target=f.exeFaceRec(s_video_filename))
        task2 = mp.Process(target=t.exeTailgating(s_video_filename))
        task3 = mp.Process(target=a.exeActivityClassification(s_video_filename))

        #start both the processes
        task1.start()
        task2.start()
        task3.start()
        num_jobs+=1

        #add all the processes
        processes.put((task1,task2,task3,s_video_filename,jid))

    print(f"The number of jobs appended are {num_jobs}")
    #job->collection of tasks:-face rec,tailgating,activity rec
    while not processes.empty():
        job = processes.get()
        num_jobs-=1
        print(f"Waiting for job {job[3]} to finish")
        #wait for processes to finish before exitting
        job[0].join()
        job[1].join()
        job[2].join()

        print(f"Done with both the job {job[-1]}")
        #delete the tpv dir's video
        
        try:
            print(f"Deleting the video after processing @ {os.path.join(tpv,job[3])}")
            os.remove(os.path.join(tpv,job[3]))
        except Exception as e:
            print(f"Deleting video Exception: {e}")

    print("Finished both all the jobs")
    doProcessing=False

t.exeTailgating("15%203.22.191.170@20200202_201109-2021-08-23_16.26.21.mp4")