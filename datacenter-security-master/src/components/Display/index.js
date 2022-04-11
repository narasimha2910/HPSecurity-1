import React, { Component } from 'react';
import { Route } from "react-router-dom";

import Home from '../Home';
import Notify from '../Notify';
import EventList from '../EventList';
import EventReport from '../EventReport';

export default class Display extends Component {
    render() {
        return (
            <div>
                <Route exact path="/" component={Home} />
                <Route path="/notify" component={Notify} />

                <Route
                    path="/tailgating"
                    component={
                        () => <EventList event_name="tailgating" />
                    }
                />

                <Route
                    path="/face_recognition"
                    component={
                        () => <EventList event_name="face_recognition" />
                    }
                />

                <Route
                    path="/activity_classifier"
                    component={
                        () => <EventList event_name="activity_classifier" />
                    }
                />

                <Route path="/report/:event/:event_name" component={EventReport} />
            </div>
        );
    }
}