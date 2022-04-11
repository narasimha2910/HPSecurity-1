import React, { Component } from "react";
import _, { filter } from "lodash";
import { saveAs } from "file-saver"
import { Box, Video, Heading, Button, Image,Spinner,Carousel } from 'grommet';
import { Download } from 'grommet-icons';
import { getEventsImages, getEventVideoSources } from "../../apis";
import { APP_SERVER_BASE } from "../../configConstants"

class EventReport extends Component {
    constructor(props) {
        super(props);
        this.state = {
            eventId: _.get(props.match.params, "event"),
            event_name: _.get(props.match.params, "event_name"),
            loading: true,
            videoElements:[],
            urls:[],
            eventImages: []
        }
    }

    //download all videos to local disk
    downloadAllVideos = ()=>{ //use arrow function as they dont redifine "this" keyword
        this.state.urls.map((vid_obj)=>{ //key->vid_name and value->vid_url
            _.forEach(vid_obj,(v,k)=>{
                saveAs(v,k);
            })
        })
    }

    // function toconvert text to asci and dash seperated format.
    //Convert '1%17.513.175.44@20200202_201109' to 49_37_49_55_46_53_49_51_46_49_55_53_46_52_52_64_50_48_50_48_48_50_48_50_95_50_48_49_49_48_57
    asciiDash(txt) {
        let res = ''
        let counter = 0
        for (let i = 0; i < txt.length; i++) {
            if (counter !== 0) {
                res = res + "_" + txt.charCodeAt(i);
            }
            else {
                res = res + txt.charCodeAt(i);
            }
            counter++;
        }
        return res;
    }

    componentDidMount() {
        const eventId = this.state.eventId;
        const event_name = this.state.event_name;

        //When component mounts,fetch the entre img in base64 format but only fetch the video file name from the server and not the video data.Make GET request from video source tag later to get the video since its a large file
        Promise.all([getEventsImages({ eventId, event_name }), getEventVideoSources({ eventId, event_name })]).then(([eventImageData, eventVideoSources]) => {
            //console.log("Recieved ImageData: " + JSON.stringify(eventImageData))

            const eventImages = [];
            _.forOwn(eventImageData, (imageData) => { //incident_id value
                _.forOwn(imageData,(images)=>{ //cam_id value
                    _.forEach(_.values(images), (imgBase64) => { //array of base64 images
                        eventImages.push(imgBase64);
                    })
                })
            });

            //equivalent to eventVideoSources[eventId]
            let if_null=[]
            const sources=_.get(eventVideoSources,eventId,if_null)

            //store all the video grommet elements and the video urls
            let urls=[];
            const videoElements = sources.map((vid_name,i)=>{
                console.log("Filename is " + vid_name);
                const videoURL = `${APP_SERVER_BASE}/event-video?event=${this.state.eventId}&source=${this.asciiDash(vid_name)}&event_name=${this.state.event_name}`;
                let vid = {};
                vid[vid_name]=videoURL;
                urls.push(vid);
                return <Box key={i} height="small" width="medium" pad="small">
                    {/* Make HTTP GET request for the video */}
                    <Video autoPlay="true">
                        <source
                            src={videoURL}
                            type="video/mp4"
                            fit="comtain"
                        />
                    </Video>
                </Box>
            })

            this.setState({
                loading: false,
                eventImages,
                videoElements,
                urls
            })
        });
    }

    render() {
        return this.state.loading === true
            ? <Box align="center"><Spinner size="large"/></Box>
            : <Box align="center" background="light-1">
                <Box align="center">
                    <Heading level="4">Incident Report</Heading>
                    <Button icon={<Download />} 
                    label="Download" 
                    onClick={this.downloadAllVideos}
                    />
                </Box>

                <Heading level="5">Video Footage</Heading>
                <Box direction="row-responsive" pad="small" background="light-2">{
                    _.map(this.state.videoElements, (vid) => {
                        return vid;
                    })
                }</Box>

                <Heading level="5">Snaphots</Heading>
                <Box height="medium" width="medium" overflow="hidden">
                    <Carousel fill>
                        {
                            //fill in with the Images
                            this.state.eventImages.map(base64URL=>{
                                 //A dataURL consists of two parts:- data media type and the base64 string of the image.A dataURL can be used as img src url
                                return (
                                <Image
                                    fit="contain"
                                    style={{ maxWidth: "100%" }}
                                    src={`data:image/jpg;base64, ${base64URL}`}
                                />
                                )
                            })
                        }
                    </Carousel>
                </Box>
            </Box>
    }
}

export default EventReport
