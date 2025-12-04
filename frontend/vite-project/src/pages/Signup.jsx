import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { signup } from "../services/authService";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Signup() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match ");
      return;
    }

    setLoading(true);
    try {
      const response = await signup({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });

      toast.success("Account created successfully 🎉");
      localStorage.setItem("authToken", response.access_token);
      setTimeout(() => navigate("/login"), 1200);
    } catch (error) {
      const message =
        error?.response?.data?.msg ||
        error?.msg ||
        "Signup failed ";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-railway-gradient relative overflow-hidden">
      {/* Animated background glows */}
      <motion.div
        className="absolute w-96 h-96 bg-primary/25 rounded-full blur-3xl top-20 left-10"
        animate={{ x: [0, 40, 0], y: [0, 35, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-[26rem] h-[26rem] bg-accent/20 rounded-full blur-3xl bottom-10 right-10"
        animate={{ x: [0, -40, 0], y: [0, -45, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      {/*  Signup form card */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md bg-card/70 backdrop-blur-2xl 
                   border border-white/10 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.4)] p-10"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
            Create an Account
          </h1>
          <p className="text-neutral-400 mt-2">
            Join your Docker deployment platform 
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Username */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-1">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              placeholder="e.g. ghitaa"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-1">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="you@example.com"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-accent outline-none transition-all"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-1">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>

          {/* Confirm password */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-accent outline-none transition-all"
            />
          </div>

          {/* Submit */}
          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.97 }}
            className="w-full py-2.5 bg-gradient-to-r from-primary to-accent 
                       text-white font-semibold rounded-lg shadow-lg hover:shadow-primary/30 
                       hover:opacity-90 transition-transform transform hover:scale-[1.02] 
                       focus:ring-4 focus:ring-primary/30"
          >
            {loading ? <LoadingSpinner size="w-6 h-6" /> : "Sign Up"}
          </motion.button>

          {/* Link to login */}
          <div className="text-center text-sm text-neutral-400 mt-4">
            Already have an account?{" "}
            <a
              href="/login"
              className="text-primary-light font-semibold hover:underline"
            >
              Log in
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
