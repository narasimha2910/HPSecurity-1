import React, { Component } from "react";
import _ from "lodash";
import { Box, Heading, Image, Text, RoutedButton } from "grommet/es6";
import { Compliance } from 'grommet-icons';
import { getEventDetails, getEventsImages } from "../../apis";
import { Spinner } from "grommet";

//Incident panel button functionality
class EventList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            eventData: [],
            eventsImages: [],
            loading: false
        }

        this.event_names = {
            "face_recognition": "Events run through Facial Recognition",
            "activity_classifier": "Events run through Activity Classification",
            "tailgating": "Events run through tailgating check"
        }
    }

    //upon mounting
    componentDidMount() {

        //wait for both functions to return
        //getEventImages called without passing an eventID
        console.log(this.props.event_name);
        Promise.all([getEventDetails(this.props.event_name), getEventsImages({ eventId: null, event_name: this.props.event_name })]).then(
            ([events, eventsImages]) => {
                console.log(`Events ${JSON.stringify(events)} hello`)
                const eventData = {};

                //combine the column name with row values
                //Eg: [incident_id:7, datetime:"Sun, 02 Feb 2020 20:11:09 GMT", source_ip:"203.22.191.170"]
                const recordsWithHeaders = _.map(events.records, (r) => {
                    return _.zipObject(events.cols, r);
                });

                _.forEach(recordsWithHeaders, r => {

                    //extract details of each incident
                    const eventId = _.get(r, "incident_id");

                    const camData = _.get(eventData, `${eventId}.camData`, []);
                    camData.push(r);
                    _.set(eventData, `${eventId}.camData`, camData);
                    const eventImageData = eventsImages[eventId];
                    console.log(`EventImagesObj:${JSON.stringify(eventsImages)}`)
                    console.log(`EventImageData:${eventImageData}`)

                    //extract the images
                    const eventImages = [];
                    _.forOwn(eventImageData, (imageData, camName) => {
                        _.forEach(_.values(imageData), (imgBase64, i) => {
                            eventImages.push(imgBase64);
                        })
                    });
                    _.set(eventData, `${eventId}.images`, eventImages);
                    // Just pick the first camera date time as event datetime
                    _.set(eventData, `${eventId}.datetime`, _.get(eventData, `${eventId}.camData[0].datetime`));
                });
                this.setState({
                    loading: false,
                    eventData: eventData
                })
                console.log(`Final event data ${JSON.stringify(this.state.eventData)}`)
            });
    }

    render() {
        return this.state.loading === true ? <Box align="center"><Spinner size="large" /></Box> : (
            <Box align="center">

                <Heading level="4" align="center"> {`List of ${this.event_names[`${this.props.event_name}`]}`}</Heading>
                <h2>Hello There</h2>
                <Box align="center">
                    <h1>Hello 2</h1>
                    {

                        _.map(_.keys(this.state.eventData), eventId => {

                            const eventDataByCams = _.get(this.state.eventData, `${eventId}.camData`);
                            console.log("Cam data " + JSON.stringify(eventDataByCams))
                            const eventImages = _.get(this.state.eventData, `${eventId}.images`);
                            console.log("The number of images is " + eventImages.length)
                            const datetime = new Date(_.get(this.state.eventData, `${eventId}.datetime`));

                            if (eventImages.length > 0) {
                                return <Box key={eventId}
                                    round="small"
                                    margin="small"
                                    pad="medium"
                                    background="light-1"
                                    height="medium"
                                    width="large">

                                    <div style={{ display: "flex", justifyContent: "center" }}>{
                                        _.map(eventImages, (imgBase64, i) => {
                                            //alert(eventImages[0])
                                            return (
                                                <Box key={i} align="center"
                                                    border={{ color: 'black', size: 'medium' }}
                                                    pad="small"
                                                >
                                                    <Image
                                                        fit="contain"
                                                        style={{ maxWidth: "100%", height: "360px", width: "360px" }}
                                                        src={`data:image/jpg;base64, ${imgBase64}`}
                                                    />
                                                </Box>
                                            )
                                        })
                                    }
                                    </div>

                                    <br />

                                    <Box direction="row" align="center">
                                        <Box>
                                            <Text>
                                                Incident ID: {`${eventDataByCams[0].incident_id}`}

                                            </Text>
                                            <Text>
                                                Date: {`${datetime.getUTCDate()}-${datetime.getUTCMonth() + 1}-${datetime.getUTCFullYear()}`}
                                            </Text>
                                            <Text>
                                                Time: {`${datetime.toLocaleTimeString()}`}
                                            </Text>
                                        </Box>

                                        <Box pad="medium">
                                            <RoutedButton icon={<Compliance />}
                                                label="View Report"
                                                path={`/report/${eventId}/${this.props.event_name}`}
                                                margin="small"
                                            />
                                        </Box>

                                    </Box>

                                </Box>
                            }
                        })
                    }</Box>
            </Box>
        )
    }
}

export default EventList;