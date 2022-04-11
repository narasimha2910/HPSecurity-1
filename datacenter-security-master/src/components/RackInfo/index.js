import React, { useState } from "react";
import { Box, Button, Spinner } from "grommet";
import getRackInfo from "../../apis/getRackInfo";

const GetRackInfo = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  return (
    <>
    {loading ? <div style={{display: "flex", width: "100vw", height: "100vw", alignItems: "center", justifyContent: "center"}}><Spinner size="xlarge"/></div>: <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Box>
        {data.length === 0 ? (
          <Button
            label="Get Information"
            size="large"
            onClick={async () => {
             setLoading(true)
             getRackInfo().then(data => {setData(data); setLoading(false)})
            }}
          />
        ) : (
          <div
            style={{
              background: "#1f1f1f",
              color: "#ffffff",
              padding: 30,
              borderRadius: "12px",
            }}
          >
            <table
              style={{
                height: "400px",
                width: "90vw",
                textAlign: "center",
              }}
            >
              <thead>
                <tr>
                  <td>Face</td>
                  <td>Location</td>
                  <td>Person Found In Rack</td>
                  <td>Video link</td>
                </tr>
              </thead>
              <tbody>
                {data.map((d, ind) => (
                  <tr key={ind}>
                    <td>
                      {d.face.map((face, ix) => (
                        <span key={ix} style={{ margin: 10, display: "block" }}>
                          {face}
                        </span>
                      ))}
                    </td>
                    <td>{d.location}</td>
                    <td>
                      {d.person_found_in_rack.map((rack, ix) => (
                        <span key={ix} style={{ margin: 10, display: "block" }}>
                          {rack}
                        </span>
                      ))}
                    </td>
                    <td>{d.video_link}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Box>
    </div>}
    
    </>
  );
};

export default GetRackInfo;
