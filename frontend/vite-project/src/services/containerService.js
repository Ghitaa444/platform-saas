import api from "./api";

/**
 * 🔹 Récupère la liste des conteneurs de l’utilisateur connecté
 */
export const getContainers = async () => {
  try {
    const response = await api.get("/api/containers/list");
    return response.data;
  } catch (error) {
    console.error("❌ Erreur lors de la récupération des conteneurs :", error);
    throw error.response?.data || error.message;
  }
};

/**
 * 🔹 Crée un nouveau conteneur Docker
 */
export const createContainer = async (containerData) => {
  try {
    const payload = {
      container_name: containerData.name?.trim(),
      image_name: containerData.image?.trim(),
      ports: containerData.ports
        ? containerData.ports
            .split(",")
            .map((p) => p.trim())
            .filter((p) => p.length > 0)
        : [],
      environment:
        typeof containerData.envVars === "string"
          ? (() => {
              try {
                return JSON.parse(containerData.envVars || "{}");
              } catch {
                console.warn("⚠️ Variables d’environnement mal formatées, ignorées.");
                return {};
              }
            })()
          : containerData.envVars || {},
    };

    console.log("🚀 Envoi payload à Flask :", payload);
    const response = await api.post("/api/containers/create", payload);
    console.log("✅ Conteneur créé :", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Erreur lors de la création du conteneur :", error);
    throw error.response?.data || error.message;
  }
};

/**
 * 🔹 Démarre un conteneur
 */
export const startContainer = async (id) => {
  try {
    const response = await api.post(`/api/containers/${id}/start`);
    return response.data;
  } catch (error) {
    console.error(`❌ Erreur lors du démarrage du conteneur ${id}:`, error);
    throw error.response?.data || error.message;
  }
};

/**
 * 🔹 Arrête un conteneur
 */
export const stopContainer = async (id) => {
  try {
    const response = await api.post(`/api/containers/${id}/stop`);
    return response.data;
  } catch (error) {
    console.error(`❌ Erreur lors de l’arrêt du conteneur ${id}:`, error);
    throw error.response?.data || error.message;
  }
};

/**
 * 🔹 Supprime un conteneur
 */
export const removeContainer = async (id) => {
  try {
    const response = await api.delete(`/api/containers/${id}/remove`);
    return response.data;
  } catch (error) {
    console.error(`❌ Erreur lors de la suppression du conteneur ${id}:`, error);
    throw error.response?.data || error.message;
  }
};

/**
 * ✅ Fonction universelle pour gérer toutes les actions (start, stop, remove)
 */
export const performAction = async (id, action) => {
  try {
    let result;

    switch (action) {
      case "start":
        result = await startContainer(id);
        break;
      case "stop":
        result = await stopContainer(id);
        break;
      case "remove":
        result = await removeContainer(id);
        break;
      default:
        throw new Error(`Action inconnue : ${action}`);
    }

    console.log(`✅ Action "${action}" effectuée sur le conteneur ${id}`);
    return result;
  } catch (error) {
    console.error(`❌ Erreur lors de l’action "${action}" sur ${id}:`, error);
    throw error;
  }
};

/**
 * 🔹 Récupère les statistiques (CPU, RAM, uptime) d’un conteneur
 */
export const getContainerStats = async (id) => {
  try {
    const response = await api.get(`/api/containers/${id}/stats`);
    return response.data; 
    // Exemple: { cpu_percent: 5.3, memory_percent: 23.1, uptime: "2m 15s" }
  } catch (error) {
    console.error(`❌ Erreur lors de la récupération des stats du conteneur ${id}:`, error);
    throw error.response?.data || error.message;
  }
};
