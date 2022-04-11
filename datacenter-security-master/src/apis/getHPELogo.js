import {APP_SERVER_BASE} from "../configConstants"

const getHPELogo = async()=>{
    const apiName = "get-logo";
    const data = await fetch(`${APP_SERVER_BASE}/${apiName}`).then(d=> d.json());
    return data.data;
};

export default getHPELogo;
