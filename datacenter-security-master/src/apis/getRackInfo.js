const getRackInfo = async () => {
    const response = await fetch('http://127.0.0.1:5000/get-grid', {
        method: "GET",
    }).then(data => data.json())
    console.log(response);
    return response
}

export default getRackInfo