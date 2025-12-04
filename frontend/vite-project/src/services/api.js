// src/api.js
import axios from "axios";

// 🌍 Détection intelligente de l’environnement (local / Docker / production)
let API_BASE_URL;

if (import.meta.env.VITE_API_URL) {
  // 🔧 Variable d’environnement définie (prioritaire)
  API_BASE_URL = import.meta.env.VITE_API_URL;
} else if (window.location.hostname === "localhost") {
  // 💻 En local
  API_BASE_URL = "http://localhost:5000/api";
} else if (window.location.hostname.includes("github.dev")) {
  // 🌐 Mode Codespaces / GitHub
  // ⚠️ Ton backend tourne sur le port 5000
  API_BASE_URL = `https://${window.location.hostname.replace("-80", "-5000")}/api`;
} else if (window.location.hostname.includes("saas_frontend")) {
  // 🐳 Environnement Docker (communication inter-containers)
  API_BASE_URL = "http://saas_backend_app:5000/api";
} else {
  // ☁️ En production (même domaine)
  API_BASE_URL = `${window.location.origin}/api`;
}

console.log("🔗 API Base URL =", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
  },
});

// 🔒 Ajout automatique du token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ⚠️ Gestion globale des erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;

      console.error("❌ API Error:", status, error.response.data);

      // 🔁 Si le token est expiré, on déconnecte automatiquement l'utilisateur
      if (status === 401 && error.response.data?.msg === "Token has expired") {
        console.warn("⚠️ Token expiré — déconnexion automatique.");
        localStorage.removeItem("authToken");
        window.location.href = "/login";
      }
    } else {
      console.error("🚨 Network Error:", error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
