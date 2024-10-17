const URL = "http://localhost:5000";

const sendRequest = async (route, content = null, method = "GET") => {
    const response = await fetch(URL + "/" + route, {
        method: method,
        body: content
    });

    return response;
}

export default sendRequest;