import psycopg2
from operator import itemgetter
import json

class dcsDB:
    def __init__(self, host, pg_user, pg_password, database):
        self.host = host
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.database = database

    # connect to the database
    def connect(self):
        self.con = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.pg_user,
            password=self.pg_password
        )

    #fetch all entry or exit camera ips
    def fetchEntryExitIps(self):
        cur = self.con.cursor()

        query_cmd = "SELECT * FROM camera_details WHERE isentraceorexit = TRUE"
        cur.execute(query_cmd)
        rows = cur.fetchall()
        cur.close()
        ips=[row[0] for row in rows]
        return ips

    def disconnect(self):
        self.con.close()

    # create 4 tables
    def createTables(self):
        try:
            cur = self.con.cursor()

            # camera details - take input during setup of application stage
            cur.execute("CREATE TABLE IF NOT EXISTS camera_details ("
                        "camera_ip INET NOT NULL PRIMARY KEY,"
                        "lab_location VARCHAR(50) NOT NULL,"
                        "rack_location VARCHAR(50) NOT NULL,"
                        "model_number VARCHAR(50) NOT NULL,"
                        "isEntraceOrExit BOOLEAN DEFAULT FALSE NOT NULL"
                        ");"
                        )

            # face recognition table
            cur.execute("CREATE TABLE IF NOT EXISTS face_recognition("
                        "incident_id INT NOT NULL PRIMARY KEY," #think abt primary key
                        "datetime TIMESTAMP NOT NULL,"
                        "source_ip INET NOT NULL REFERENCES camera_details(camera_ip),"
                        "unknownCount SMALLINT,"
                        "unknownFrameNumbers JSONB"
                        ");"
                        )

            # Tailgating table
            cur.execute("CREATE TABLE IF NOT EXISTS tailgating ("
                        "incident_id INT NOT NULL PRIMARY KEY,"
                        "datetime TIMESTAMP NOT NULL,"
                        "source_ip INET NOT NULL REFERENCES camera_details(camera_ip)"
                        ");"
                        )

            # Activity Table
            cur.execute("CREATE TABLE IF NOT EXISTS activity ("
                        "incident_id INT NOT NULL PRIMARY KEY,"
                        "datetime TIMESTAMP NOT NULL,"
                        "source_ip INET NOT NULL REFERENCES camera_details(camera_ip),"
                        "activity_name VARCHAR(50)"
                        ");"
                        )

            cur.close()
            self.con.commit()
            print("Successfully created tables..")

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            pass


    # This will take in an object representing the column names and the values to perform INSERT INTO operation
    '''
    1 -> face Recognition
    2 -> tailgating
    3 -> Activity Recognition
    '''
    #{int,python list}
    def insertIncident(self, incident_type, incident_details):
        # extract common details
        incident_id, datetime, source_ip = itemgetter(
            'incident_id', 'datetime', 'source_ip')(incident_details)

        if(incident_type == 1):
            unknownCount,unknownFacesFrameNumbers = itemgetter('unknownCount','unknownFacesFrameNumbers')(incident_details)

            cur = self.con.cursor()

            #convert the array into json object string
            json_o = {"fnos":unknownFacesFrameNumbers}
            frameString = f"'{json.dumps(json_o)}'"
            print(f"The frame number array is {frameString}")

            cur.execute("INSERT INTO face_recognition(incident_id, datetime,source_ip,unknownCount,unknownFrameNumbers) "
                        "VALUES (%s, %s, %s, %s, %s)" % (f"'{str(incident_id)}'", f"'{str(datetime)}'", f"'{str(source_ip)}'", f"'{str(unknownCount)}'", frameString))
            self.con.commit()

        elif(incident_type == 2):
            cur = self.con.cursor()
            cur.execute("INSERT INTO tailgating (incident_id, datetime,source_ip) "
                        "VALUES (%s,%s,%s)" % (f"'{str(incident_id)}'", f"'{str(datetime)}'", f"'{str(source_ip)}'"))
            self.con.commit()

        elif(incident_type == 3):
            activity_name = itemgetter('activity_name')(incident_details)

            cur = self.con.cursor()
            cur.execute("INSERT INTO activity (incident_id, datetime,source_ip,activity_name) "
                        "VALUES (%s,%s,%s,%s)" % (f"'{str(incident_id)}'", f"'{str(datetime)}'", f"'{str(source_ip)}'", f"'{str(activity_name)}'"))
            self.con.commit()

    def insertCamDetails(self, details):
        cam_ip, lab_loc, rack_loc, model_no,isEntraceOrExit = itemgetter(
             'cam_ip', 'lab_loc', 'rack_loc', 'model_no','isEntraceOrExit')(details)
        cur = self.con.cursor()
        cur.execute("INSERT INTO camera_details (camera_ip,lab_location,rack_location,model_number,isEntraceOrExit)"
                    "VALUES (%s,%s,%s,%s,%s)" % (f"'{str(cam_ip)}'", f"'{str(lab_loc)}'", f"'{str(rack_loc)}'", f"'{str(model_no)}'",f"'{str(isEntraceOrExit)}'"))
        self.con.commit()


if __name__ == "__main__":
    db = dcsDB('localhost','postgres','chandra69chandra','dcsdb')

    db.connect()
    #print(db.fetchEntryExitIps())

    db.createTables()

    # #details of all the camera
    db.insertCamDetails({'cam_ip':'208.98.192.170', 'lab_loc':'f1', 'rack_loc':'r1', 'model_no':'n70','isEntraceOrExit':'TRUE'})
    db.insertCamDetails({'cam_ip':'207.96.155.171', 'lab_loc':'f2', 'rack_loc':'r1', 'model_no':'n71','isEntraceOrExit':'FALSE'})
    db.insertCamDetails({'cam_ip':'206.11.143.172', 'lab_loc':'f1', 'rack_loc':'r3', 'model_no':'n72','isEntraceOrExit':'TRUE'})
    db.insertCamDetails({'cam_ip':'203.22.191.170', 'lab_loc':'f3', 'rack_loc':'r6', 'model_no':'n70','isEntraceOrExit':'TRUE'})

    #incident incidents to test if insertion functions above are successfully executed
    # db.insertIncident(1,{'incident_id':6, 'datetime':'2020-02-02 20:11:09', 'source_ip':'208.98.192.170','unknownCount':'1','unknownFacesFrameNumbers':[2,4,6,8,10,12,14,16,18,20,22,24]}) #face_Det_algo output to test storing in db
    # db.insertIncident(1,{'incident_id':7, 'datetime':'2020-02-02 20:11:09', 'source_ip':'203.22.191.170','unknownCount':'2','unknownFacesFrameNumbers':[[2, 4, 6, 8, 10, 12], [2, 4, 6, 8, 10, 12]]})
    
    db.disconnect()





# def insertEmployeeDetail(self, details):
    #     n = int(input("Enter user rack number"))
    #     m = input("Enter user name")
    #     i = input("Enter image path")
    #     addRackUser(n, m, i)

    #     rack_num, emp_name, face_encoding = itemgetter(
    #         'rack_num', 'emp_name', 'face_encoding')(details)
    #     cur.execute("INSERT INTO employees (employee_name,employee_number,facial_encoding,alowed_rack)"
    #                 "VALUES (%s,%s,%s,%s)" % (str(id), str(cam_ip), str(lab_loc), str(model_no)))
    #     self.con.commit()


'''frameString = "'{"
            n = len(unknownFacesFrameNumbers)-1
            for i,frameNum in enumerate(unknownFacesFrameNumbers):
                if i!=n:
                    frameString += (f"{frameNum},")
                else:
                    frameString += (f"{frameNum}"+"}'")
            print(f"The frame numbers in string format is {frameString}")'''





