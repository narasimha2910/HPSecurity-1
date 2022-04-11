import React from 'react'
import { Box, Button } from "grommet/es6";
import getRackInfo from "./datacenter-security-master/src/apis/getRackInfo"

const RackInfo = () => {
    return (
        <div style={{ display: "flex", alignItems: "center", width: "100vw", height: "100vh", justifyContent: "center" }}>
            <Box><h1><Button label="Get Information" onClick={() => {
                const res = getRackInfo();
                console.log(res)
            }} /></h1></Box>
        </div>
    )
}

export default RackInfo