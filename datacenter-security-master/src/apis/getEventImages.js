import _ from "lodash";
import { APP_SERVER_BASE } from "../configConstants"

//Single image(when eventID is supplied) or all images can be fetched from server
const getEventsImages = async ({ eventId, event_name }) => {
    const apiName = "get-events-images";

    //localhost:5000/get-events-images?event_name=<event_name> or localhost:5000/get-events-images?event=2&<event_name=event_name>

    console.log("To fetch: " + `${APP_SERVER_BASE}/${apiName}${eventId ? `?event=${eventId}&event_name=${event_name}` : `?event_name=${event_name}`}`);

    const data = await fetch(`${APP_SERVER_BASE}/${apiName}${eventId ? `?event=${eventId}&event_name=${event_name}` : `?event_name=${event_name}`}`).then(d => d.json());


    /*
     console.log("To fetch: " + `${APP_SERVER_BASE}/${apiName}${eventId ? `?event=${eventId}` : ''}`);
 
     const data = await fetch(`${APP_SERVER_BASE}/${apiName}${eventId ? `?event=${eventId}` : ''}`).then(d => d.json());
 
     console.log(`Data-[getEventImages]: ${JSON.stringify(data)}`);
    */

    //loadash.get will fetch the value for query key from an object
    /*if (eventId) {
        return _.get(data, `data.${eventId}`)
    } else {
        return _.get(data, "data");
    }*/

    /*******THERE WAS A DIFFERENT LOGIC AS SHOWN ABOVE ******/
    return _.get(data, "data");
};

export default getEventsImages;