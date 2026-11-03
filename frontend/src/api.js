import axios from "axios";

const rawBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const baseURL = rawBase.endsWith("/api") ? rawBase.slice(0, -4) : rawBase;

const API = axios.create({
    baseURL: baseURL,
    timeout: 60000
});

export default API;
