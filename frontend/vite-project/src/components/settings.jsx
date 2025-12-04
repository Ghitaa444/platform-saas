// src/pages/Settings.jsx
import React, { useState } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../hooks/useAuth";
import Navbar from "../components/Navbar";
import { toast } from "react-toastify";
import { FaUser, FaEnvelope, FaLock, FaSave } from "react-icons/fa";

export default function Settings() {
  const { user, logout } = useAuth();
  const [form, setForm] = useState({
    name: user?.name || "User",
    email: user?.email || "example@email.com",
    password: "",
  });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSave = (e) => {
    e.preventDefault();
    toast.success("Profile updated successfully ", { position: "top-right" });
  };

  return (
    <div className="min-h-screen bg-railway-gradient text-text">
      <Navbar />

      <div className="pt-24 px-6 md:px-12 flex justify-center">
        <motion.form
          onSubmit={handleSave}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-xl bg-card/70 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.3)] p-8 space-y-6"
        >
          <h1 className="text-3xl font-bold text-text-light mb-6">Account Settings ⚙️</h1>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaUser /> Name
            </label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaEnvelope /> Email
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-neutral-300">
              <FaLock /> New Password
            </label>
            <input
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
              className="w-full px-4 py-2 rounded-lg bg-neutral-900/50 border border-white/10 text-text-light focus:ring-2 focus:ring-primary outline-none transition"
            />
          </div>

          <div className="flex justify-between items-center pt-6">
            <button
              type="submit"
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-primary to-accent text-white rounded-lg shadow-glow transition"
            >
              <FaSave /> Save
            </button>
            <button
              type="button"
              onClick={logout}
              className="text-red-400 hover:text-red-300 text-sm font-medium transition"
            >
              Logout
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}
