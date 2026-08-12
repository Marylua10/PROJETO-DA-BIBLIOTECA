const API_ORIGIN = window.location.port === "5000" ? "" : "http://127.0.0.1:5000";

function apiUrl(path) {
    return path.startsWith("/api/") ? `${API_ORIGIN}${path}` : path;
}
