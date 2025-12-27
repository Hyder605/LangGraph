import axios from 'axios';

// Access environment variable for your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://203.241.246.178:8000/';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
