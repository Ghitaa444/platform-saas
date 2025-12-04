import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { FaDocker, FaCogs, FaNetworkWired, FaSave } from "react-icons/fa";
import { createContainer } from "../services/containerService";

export default function CreateContainerPage() {
  const [form, setForm] = useState({
    name: "",
    image: "",
    ports: "",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 🔹 Appel à ton backend
      const response = await createContainer(form);
      toast.success(`✅ Container "${form.name}" créé avec succès !`);
      console.log("Réponse backend:", response);

      // 🔹 Reset du formulaire
      setForm({ name: "", image: "", ports: "" });
    } catch (error) {
      console.error("❌ Erreur création conteneur:", error);
      toast.error(`Échec de la création : ${error.message || error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-railway-gradient text-text">
      <Navbar />

      <div className="pt-24 px-6 md:px-12 flex justify-center">
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-xl bg-card/70 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.3)] p-8 space-y-6"
        >
          <h1 className="text-3xl font-bold text-text-light mb-6 flex items-center gap-2">
            <FaDocker className="text-primary-light" /> Create Container
          </h1>

          {/* 🔸 Nom */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaCogs /> Container Name
            </label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              placeholder="my-container"
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          {/* 🔸 Image */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaDocker /> Docker Image
            </label>
            <input
              type="text"
              name="image"
              value={form.image}
              onChange={handleChange}
              required
              placeholder="nginx:latest"
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          {/* 🔸 Ports */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaNetworkWired /> Ports
            </label>
            <input
              type="text"
              name="ports"
              value={form.ports}
              onChange={handleChange}
              placeholder="80:8080"
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          <div className="pt-6 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg shadow-glow transition ${
                loading
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-primary to-accent text-white hover:opacity-90"
              }`}
            >
              <FaSave /> {loading ? "Deploying..." : "Deploy"}
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}
