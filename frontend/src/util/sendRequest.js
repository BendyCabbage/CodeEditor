const BASE_URL = "http://localhost:5000/";

const sendRequest = async (route, options = {}) => {
    const { method = "GET", body = null, json = false } = options;
    
    const fetchOptions = {
        method: method,
    };
    
    if (body !== null) {
        if (json) {
            fetchOptions.headers = {
                'Content-Type': 'application/json',
            };
            fetchOptions.body = JSON.stringify(body);
        } else {
            fetchOptions.body = body;
        }
    }
    
    const response = await fetch(BASE_URL + route, fetchOptions);
    return response;
};

export const api = {
    createProject: async (name) => {
        const res = await sendRequest('projects', { method: 'POST', body: { name }, json: true });
        return res.json();
    },
    
    cloneProject: async (githubUrl, name = null) => {
        const body = { github_url: githubUrl };
        if (name) body.name = name;
        const res = await sendRequest('projects/clone', { method: 'POST', body, json: true });
        return res.json();
    },
    
    getProject: async (projectId) => {
        const res = await sendRequest(`projects/${projectId}`);
        return res.json();
    },
    
    getProjectTree: async (projectId) => {
        const res = await sendRequest(`projects/${projectId}/tree`);
        return res.json();
    },
    
    getFile: async (projectId, filePath) => {
        const res = await sendRequest(`projects/${projectId}/files/${filePath}`);
        return res.json();
    },
    
    saveFile: async (projectId, filePath, content) => {
        const res = await sendRequest(`projects/${projectId}/files/${filePath}`, {
            method: 'PUT',
            body: { content },
            json: true
        });
        return res.json();
    },
    
    createFile: async (projectId, path, isDirectory = false) => {
        const res = await sendRequest(`projects/${projectId}/files`, {
            method: 'POST',
            body: { path, is_directory: isDirectory },
            json: true
        });
        return res.json();
    },
    
    deleteFile: async (projectId, filePath) => {
        const res = await sendRequest(`projects/${projectId}/files/${filePath}`, {
            method: 'DELETE'
        });
        return res.json();
    }
};

export default sendRequest;