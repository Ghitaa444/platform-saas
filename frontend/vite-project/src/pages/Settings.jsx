import React, { useState } from "react";
import { motion } from "framer-motion";
import Navbar from "../components/Navbar";
import { FaUserEdit, FaLock } from "react-icons/fa";

export default function Settings() {
  const [activeTab, setActiveTab] = useState("profile");

  const renderContent = () => {
    if (activeTab === "profile") {
      return (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-card/70 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.3)] p-8"
        >
          <h2 className="text-2xl font-semibold text-text-light mb-6 flex items-center gap-2">
            <FaUserEdit className="text-primary-light" /> Profile Settings
          </h2>

          <form className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-1">
                Username
              </label>
              <input
                type="text"
                placeholder="Your name"
                className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/50 border border-white/10 text-text focus:ring-2 focus:ring-primary outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-1">
                Email Address
              </label>
              <input
                type="email"
                placeholder="your@email.com"
                className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/50 border border-white/10 text-text focus:ring-2 focus:ring-primary outline-none transition"
              />
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              className="w-full py-2.5 bg-gradient-to-r from-primary to-accent text-white font-semibold rounded-lg shadow-glow hover:opacity-90 transition"
            >
              Save Changes
            </motion.button>
          </form>
        </motion.div>
      );
    }

    if (activeTab === "security") {
      return (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-card/70 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.3)] p-8"
        >
          <h2 className="text-2xl font-semibold text-text-light mb-6 flex items-center gap-2">
            <FaLock className="text-accent-light" /> Security
          </h2>

          <form className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-1">
                Current Password
              </label>
              <input
                type="password"
                placeholder="********"
                className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/50 border border-white/10 text-text focus:ring-2 focus:ring-accent outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-1">
                New Password
              </label>
              <input
                type="password"
                placeholder="********"
                className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/50 border border-white/10 text-text focus:ring-2 focus:ring-accent outline-none transition"
              />
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              className="w-full py-2.5 bg-gradient-to-r from-accent to-primary text-white font-semibold rounded-lg shadow-glow hover:opacity-90 transition"
            >
              Change Password
            </motion.button>
          </form>
        </motion.div>
      );
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
          className="text-3xl font-bold text-text-light mb-8"
        >
           Settings
        </motion.h1>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar interne */}
          <div className="w-full md:w-1/4">
            <nav className="flex flex-col space-y-2 bg-card/70 backdrop-blur-xl border border-white/10 p-4 rounded-xl shadow-[0_4px_30px_rgba(0,0,0,0.3)]">
              <button
                onClick={() => setActiveTab("profile")}
                className={`flex items-center px-4 py-2.5 rounded-lg font-medium transition-all ${
                  activeTab === "profile"
                    ? "bg-gradient-to-r from-primary to-accent text-white shadow-glow"
                    : "text-neutral-400 hover:bg-neutral-900/50 hover:text-text-light"
                }`}
              >
                <FaUserEdit className="mr-3" /> Profile
              </button>

              <button
                onClick={() => setActiveTab("security")}
                className={`flex items-center px-4 py-2.5 rounded-lg font-medium transition-all ${
                  activeTab === "security"
                    ? "bg-gradient-to-r from-primary to-accent text-white shadow-glow"
                    : "text-neutral-400 hover:bg-neutral-900/50 hover:text-text-light"
                }`}
              >
                <FaLock className="mr-3" /> Security
              </button>
            </nav>
          </div>

          {/* Contenu dynamique */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="flex-1"
          >
            {renderContent()}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
