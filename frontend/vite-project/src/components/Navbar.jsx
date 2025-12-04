// src/components/Navbar.jsx
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { FaDocker } from "react-icons/fa";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navItems = [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Containers", path: "/create-container" },
    { label: "Settings", path: "/settings" },
  ];

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="fixed top-0 left-0 right-0 z-50 bg-card/70 backdrop-blur-xl border-b border-white/10
                 shadow-[0_8px_32px_rgba(31,38,135,0.2)] text-text"
    >
      <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
        {/* ---- LOGO ---- */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-tr from-primary to-accent text-white rounded-xl shadow-glow">
            <FaDocker className="text-xl" />
          </div>
          <h1 className="text-lg font-bold tracking-wide bg-gradient-to-r from-primary to-accent text-transparent bg-clip-text">
            SaaS Platform
          </h1>
        </div>

        {/* ---- NAVIGATION ---- */}
        <nav className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `relative text-sm font-medium transition hover:text-primary ${
                  isActive ? "text-primary" : "text-gray-400"
                }`
              }
            >
              {item.label}
              {({ isActive }) =>
                isActive && (
                  <motion.span
                    layoutId="underline"
                    className="absolute -bottom-1 left-0 right-0 h-[2px] bg-primary rounded-full"
                  />
                )
              }
            </NavLink>
          ))}
        </nav>

        {/* ---- ACTION BUTTONS ---- */}
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <span className="hidden md:inline text-gray-400 text-sm">
                {user.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate("/login")}
                className="text-sm text-gray-400 hover:text-primary transition"
              >
                Sign in
              </button>
              <button
                onClick={() => navigate("/signup")}
                className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-primary to-accent rounded-lg text-white shadow-glow hover:opacity-90 transition"
              >
                Sign up
              </button>
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
}
