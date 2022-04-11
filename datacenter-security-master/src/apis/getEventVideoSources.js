import { APP_SERVER_BASE } from "../configConstants"

//only get the video file names and not the entore video.
//Let the video src tag fet the video
const getEventVideoSources = async ({ eventId, event_name }) => {
    const apiName = "get-event-video-sources";
    const data = await fetch(`${APP_SERVER_BASE}/${apiName}?event=${eventId}&event_name=${event_name}`).then(d => d.json());
    console.log(data);
    return data.data;
};

export default getEventVideoSources;
