import React, { Component } from 'react';
import { Box, RoutedButton } from 'grommet';

//sidebar
export default class Index extends Component {
  render() {
    return (
      /*Home button on sidebar*/
      <Box align="center" pad="small" flex>
        <RoutedButton label="Home" path="/" margin="small" />

        {/*Incidents panel button on sidebar*/}
        <RoutedButton label="Incidents Panel" path="/incidents" margin="small" />

        {/*Infrmation cneter button on sidebar*/}
        <RoutedButton label="Information Center" path="/notify" margin="small" />
      </Box>
    );
  }

}
