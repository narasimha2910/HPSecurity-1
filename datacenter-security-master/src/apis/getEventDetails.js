import { APP_SERVER_BASE } from "../configConstants"

const getEventDetails = async (event_name) => {
    const apiName = "get-events";

    //make api request to app server
    const data = await fetch(`${APP_SERVER_BASE}/${apiName}?event_name=${event_name}`)
        .then(d => d.json());
    console.log("The data sent from server is " + JSON.stringify(data));
    return data.data;
};

export default getEventDetails;

/*
The data sent from server when no "event_type" scheme:-
{
    "data":
    {
        "cols":["id","timestamp","incident_id","source_ip","datetime","person_count","known_count","people"],
        "records":[
            [1,"Fri, 02 Jul 2021 00:18:54 GMT","1","15.213.155.94","Sun, 02 Feb 2020 20:11:09 GMT",2,2,["akshay","akshay"]],
            [2,"Fri, 02 Jul 2021 00:19:16 GMT","1","15.213.155.94","Sun, 02 Feb 2020 20:11:09 GMT",2,2,["akshay","akshay"]]
        ]

    }

}
*/