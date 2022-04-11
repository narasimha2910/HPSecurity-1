import React, { Component } from 'react';

import Image1 from "../../Images/puc.jpg"

export default class Notify extends Component {
    render() {
        return (
            <div>
                New notifications about the portal for the clients
                <br/><br/>
                <img
                    src={Image1}
                    width='100%'
                    height='100%'/>
            </div>
        );
    }

}