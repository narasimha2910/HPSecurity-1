import React, { Component } from 'react';
import { Box, RoutedButton, Heading } from 'grommet';

//this is the content following the title bar which contains the incident panel button
export default class Home extends Component {
    render() {
        return (
            <Box align="center" justify="center">
                <br /><br /><br /><br /><br /><br /><br /><br /><br />
                <Heading level="3">Hewlett Packard Enterprise - Data Center Security</Heading>
                <Heading level="4">Browse Incidents</Heading>

                <RoutedButton label="Tailgating Panel" path="/tailgating" margin="small" />

                <RoutedButton label="Facial Recognition" path="/face_recognition" margin="small" />
                
                <RoutedButton label="Activity Classifier" path="/activity_classifier" margin="small" />

                <Box align="center" justify="center">
                    
                </Box>
            </Box>
        );
    }

}
