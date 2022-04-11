import { APP_SERVER_BASE } from "./datacenter-security-master/src/configConstants"

const getGridInfo = async () => {
    const data = {}
    await fetch(`http://127.0.0.1:5000/get-grid`, {
        method: "GET",
        mode: "no-cors"
    }).then(res => res.json()).then(data => data = data)
    return data;
}

export default getGridInfo;