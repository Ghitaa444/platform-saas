import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { login as loginUser } from "../services/authService";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await loginUser({ username, password });

      // ✅ Use consistent key name with api.js
      localStorage.setItem("authToken", response.access_token);

      toast.success("Connexion réussie !");
      navigate("/dashboard");
    } catch (error) {
      console.error("Login error:", error);
      toast.error(error.msg || "Échec de la connexion");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-railway-gradient relative overflow-hidden">
      {/* Animated background circles */}
      <motion.div
        className="absolute w-80 h-80 bg-primary/20 rounded-full blur-3xl top-24 left-20"
        animate={{ x: [0, 25, 0], y: [0, 30, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-96 h-96 bg-accent/25 rounded-full blur-3xl bottom-20 right-20"
        animate={{ x: [0, -20, 0], y: [0, -25, 0] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Main card */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md bg-card/70 backdrop-blur-2xl 
                   border border-white/10 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.4)] p-10"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
            Welcome Back
          </h1>
          <p className="text-neutral-400 mt-2">
            Log in to access your dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter your username"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="********"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-accent outline-none transition-all"
            />
          </div>

          <div className="text-right">
            <a
              href="/forgot-password"
              className="text-sm text-primary-light font-medium hover:underline"
            >
              Forgot password?
            </a>
          </div>

          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.97 }}
            className="w-full py-2.5 bg-gradient-to-r from-primary to-accent 
                       text-white font-semibold rounded-lg shadow-lg hover:shadow-primary/30 
                       hover:opacity-90 transition-transform transform hover:scale-[1.02] 
                       focus:ring-4 focus:ring-primary/30"
          >
            {loading ? <LoadingSpinner size="w-6 h-6" /> : "Log In"}
          </motion.button>

          <div className="text-center text-sm text-neutral-400 mt-4">
            No account yet?{" "}
            <a
              href="/signup"
              className="text-primary-light font-semibold hover:underline"
            >
              Sign up
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
