import React, { Component } from 'react';
import { Box, Button, Collapsible, Heading, Grommet, Layer, ResponsiveContext, Image } from 'grommet';
import { FormClose, Sort } from 'grommet-icons';
import { BrowserRouter as Router } from "react-router-dom";

import Index from './components/Nav';
import Display from './components/Display';
import RackInfo from './components/RackInfo';
import { getHPELogo } from "./apis";

import './components/Nav/nav.css';

//This is the Home Page

const theme = {
    global: {
        colors: {
            brand: '#4b5e6b',
        },
        font: {
            family: 'Roboto',
            size: '14px',
            height: '20px',
        },
    },
};

const AppBar = (props) => (
    <Box
        tag='header'
        direction='row'
        align='center'
        justify='between'
        background='brand'
        pad={{ left: 'medium', right: 'small', vertical: 'small' }}
        elevation='medium'
        style={{ zIndex: '1' }}
        {...props}
    />
);


//This is only the Title bar and side bar
class App extends Component {
    state = {
        showSidebar: false,
        logoImgBase64: null
    };
    componentDidMount() {
        getHPELogo().then((logoImgBase64) => {
            this.setState({
                logoImgBase64
            })
        })
    }

    render() {
        const { showSidebar } = this.state;
        return (
            <Router>
                <Grommet theme={theme} full>
                    <ResponsiveContext.Consumer>
                        {size => (
                            <Box fill>
                                <AppBar>

                                    {/*sidebar opening button*/}
                                    <Button
                                        icon={<Sort />}
                                        onClick={() => this.setState({ showSidebar: !this.state.showSidebar })}
                                    />

                                    {/*project heading*/}
                                    <Heading level='3' margin='none'>
                                        <Box flex align='center' justify='center' pad='small'>
                                            Data Center Security Project
                                        </Box>
                                    </Heading>

                                    {/*hpe logo on right*/}
                                    <Heading level='3' margin='none'>
                                        <Box direction='row' flex overflow={{ horizontal: 'hidden' }}>
                                            <Box>
                                                <Image
                                                    src={`data:image/svg+xml;base64, ${this.state.logoImgBase64}`}
                                                    width='150px'
                                                    height='60px' />
                                            </Box>
                                        </Box>
                                    </Heading>

                                </AppBar>

                                {/*sidebar when open*/}
                                <Box direction='row' flex overflow={{ horizontal: 'hidden' }}>

                                    {(!showSidebar || size !== 'small') ? (
                                        <Collapsible direction="horizontal" open={showSidebar}>
                                            <Box
                                                width='medium'
                                                background='light-2'
                                                elevation='small'
                                                justify='top'
                                                basis='full'
                                                height="100%"
                                                overflow={{ vertical: 'hidden' }}
                                            >
                                                <Index />
                                            </Box>
                                        </Collapsible>
                                    ) : (
                                        <Layer>
                                            <Box
                                                background='light-2'
                                                tag='header'
                                                justify='end'
                                                align='center'
                                                direction='row'
                                            >
                                                <Button
                                                    icon={<FormClose />}
                                                    onClick={() => this.setState({ showSidebar: false })}
                                                />
                                            </Box>
                                            <Box
                                                fill
                                                background='light-2'
                                                align='center'
                                                justify='center'
                                            >
                                                <Index />
                                            </Box>
                                        </Layer>
                                    )}

                                    <Box flex
                                        overflow={{ "vertical": "scroll", "horizontal": "hidden" }}
                                        height="100%"
                                    >
                                        {/* <Display /> */}
                                        <RackInfo />
                                    </Box>

                                </Box>
                            </Box>
                        )}
                    </ResponsiveContext.Consumer>
                </Grommet>
            </Router>
        );
    }
}

export default App;
