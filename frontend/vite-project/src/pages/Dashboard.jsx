import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ContainerCard from "../components/ContainerCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { motion } from "framer-motion";
import { getContainers, performAction, getContainerStats } from "../services/containerService";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function Dashboard() {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 🔹 Fetch container list
  const fetchContainers = async () => {
    try {
      const data = await getContainers();
      const list = data.containers || data || [];
      setContainers(list);
      setError(null);
    } catch (err) {
      console.error("Erreur lors du chargement des conteneurs :", err);
      setError("Impossible de charger les conteneurs. Vérifie que le backend est bien en ligne.");
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Fetch stats for all containers
  const updateStats = async () => {
    try {
      const updated = await Promise.all(
        containers.map(async (container) => {
          try {
            const stats = await getContainerStats(container.docker_id || container.Id);
            return {
              ...container,
              cpu: `${stats.cpu_percent?.toFixed(1) || 0}%`,
              memory: `${stats.memory_percent?.toFixed(1) || 0}%`,
              uptime: stats.uptime || container.Status || "—",
              cpuHistory: [...(container.cpuHistory || []), stats.cpu_percent || 0].slice(-15),
              ramHistory: [...(container.ramHistory || []), stats.memory_percent || 0].slice(-15),
            };
          } catch {
            return container;
          }
        })
      );
      setContainers(updated);
    } catch (err) {
      console.warn("Erreur lors de la mise à jour des stats :", err);
    }
  };

  // 🔁 Initial load + refresh
  useEffect(() => {
    fetchContainers();
  }, []);

  // 🔄 Update stats every 5 seconds
  useEffect(() => {
    if (containers.length > 0) {
      const interval = setInterval(updateStats, 5000);
      return () => clearInterval(interval);
    }
  }, [containers]);

  // 🟢 Start
  const handleStart = async (id) => {
    try {
      toast.info("Démarrage du conteneur...");
      await performAction(id, "start");
      toast.success("Conteneur démarré ✅");
      fetchContainers();
    } catch {
      toast.error("Échec du démarrage ❌");
    }
  };

  // 🔴 Stop
  const handleStop = async (id) => {
    try {
      toast.info("Arrêt du conteneur...");
      await performAction(id, "stop");
      toast.success("Conteneur arrêté 💤");
      fetchContainers();
    } catch {
      toast.error("Erreur lors de l’arrêt ❌");
    }
  };

  // 🗑️ Delete
  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer ce conteneur ?")) return;
    try {
      toast.info("Suppression du conteneur...");
      await performAction(id, "remove");
      toast.success("Conteneur supprimé 🗑️");
      fetchContainers();
    } catch {
      toast.error("Erreur lors de la suppression ❌");
    }
  };

  return (
    <div className="min-h-screen bg-railway-gradient text-text">
      <Navbar />
      <div className="pt-24 px-6 md:px-12">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-3xl font-bold text-text-light mb-6"
        >
          Dashboard
        </motion.h1>

        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/10 border border-red-500 text-red-400 rounded-xl p-4 max-w-lg"
          >
            {error}
          </motion.div>
        ) : containers.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-gray-400 mt-10"
          >
            Aucun conteneur n’a encore été déployé.
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
          >
            {containers.map((container, i) => (
              <ContainerCard
                key={container.Id || container.docker_id || i}
                id={container.docker_id || container.Id || i}
                name={container.Names?.[0]?.replace("/", "") || container.name}
                image={container.Image || container.image}
                cpu={container.cpu}
                memory={container.memory}
                cpuHistory={container.cpuHistory}
                ramHistory={container.ramHistory}
                ports={
                  container.Ports?.map(
                    (p) => `${p.PublicPort || p.PrivatePort}:${p.PrivatePort}`
                  ).join(", ") ||
                  (Array.isArray(container.ports)
                    ? container.ports.join(", ")
                    : container.ports) ||
                  "—"
                }
                uptime={container.uptime || container.Status || "—"}
                status={
                  container.State === "running" ||
                  container.status === "running"
                    ? "running"
                    : "stopped"
                }
                onStart={handleStart}
                onStop={handleStop}
                onRemove={handleDelete}
              />
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
