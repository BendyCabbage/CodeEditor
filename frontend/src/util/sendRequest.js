const URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8080/";

const sendRequest = async (route, content = null, method = "GET") => {
    const response = await fetch(URL + route, {
        method: method,
        body: content
    });

    return response;
}

export default sendRequest;