import psycopg2
from decouple import config

actiity_table_map = {
    "activity_classifier":"activity",
    "tailgating":"tailgating",
    "face_recognition":"face_recognition",
    "test_locations":"test_locations"
}

class DbHandler:
    def __init__(self, config):
        self.conn_str = f"dbname={config('POSTGRES_DB')} user={config('POSTGRES_USER')} " \
            f"password={config('POSTGRES_PASSWORD')} host={config('POSTGRES_HOST')} port={config('POSTGRES_PORT')}"

    def connectToDB(self):
        self.connection = psycopg2.connect(self.conn_str)

    def disconnectFromDb(self):
        self.connection.close()

    # add method to query from a particular table
    def getEvents(self,activityName):
        tableName=actiity_table_map[activityName]
        cur = self.connection.cursor()
        fetch_incidents_query = f"SELECT * FROM {tableName}"
        cur.execute(fetch_incidents_query)

        #extract ran array of rows
        rows = cur.fetchall()
        print("Rows")
        # for row in rows:
        #     print(row)

        colnames = [desc[0] for desc in cur.description]
        
        return {
            "records":rows,
            "cols":colnames
        }

    def getRack(self, ip_addr):
        cur = self.connection.cursor()
        fetch_incidents_query = f"SELECT * FROM test_locations WHERE ip_address='{ip_addr}'"
        cur.execute(fetch_incidents_query)
        rows = cur.fetchall()
        print(rows)
        # colnames = [desc[0] for desc in cur.description]
        sql_list = []
        for row in rows[0]:
            sql_list.append(row)
        sql_dict = {}
        i = 0
        for desc in cur.description:
            sql_dict[desc[0]] = sql_list[i]
            i += 1
        return sql_dict

if __name__ == "__main__":
    dbHandler = DbHandler(config)
    dbHandler.connectToDB()
    #length of each element in "rows" array == length of "cols" array
    db = dbHandler.getEvents('face_recognition')
    print(db)
    dbHandler.disconnectFromDb()


















    # def getEvents(self, event_name):
    #     cursor = self.connection.cursor()
    #     # fetch all incidnts from database
    #     fetch_incidents_query = "SELECT * FROM incidents"
    #     cursor.execute(fetch_incidents_query)
    #     incident_records = cursor.fetchall()
    #     colnames = [desc[0] for desc in cursor.description]
    #     cursor.close()
    #     return {
    #         "records": incident_records,
    #         "cols": colnames
    #     }