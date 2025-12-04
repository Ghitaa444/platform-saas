import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { useNavigate, useParams } from "react-router-dom";
import { resetPassword } from "../services/authService";
import LoadingSpinner from "../components/LoadingSpinner";

export default function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { token } = useParams();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match ");
      return;
    }

    setLoading(true);

    try {
      await resetPassword({ token, new_password: password });
      toast.success("Password successfully reset ");
      navigate("/login");
    } catch (error) {
      if (error.response?.status === 404) {
        toast.info("Password reset feature not yet available ");
      } else {
        toast.error(
          error?.msg ||
            error?.message ||
            "Error while resetting password "
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-railway-gradient relative overflow-hidden">
      {/*  Animated background circles */}
      <motion.div
        className="absolute w-80 h-80 bg-primary/20 rounded-full blur-3xl top-24 left-16"
        animate={{ x: [0, 25, 0], y: [0, 35, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-96 h-96 bg-accent/25 rounded-full blur-3xl bottom-16 right-20"
        animate={{ x: [0, -25, 0], y: [0, -30, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      {/*  Glass form card */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md bg-card/70 backdrop-blur-2xl 
                   border border-white/10 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.4)] p-10"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
            Reset your password
          </h1>
          <p className="text-neutral-400 mt-2">
            Enter a new secure password 
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* New password */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-2">
              New password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="********"
              className="w-full px-4 py-2.5 rounded-lg bg-neutral-900/60 border border-white/10 
                         text-text focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>

          {/* Confirm password */}
          <div>
            <label className="block text-sm font-semibold text-neutral-400 mb-2">
              Confirm password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="********"
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
            {loading ? <LoadingSpinner size="w-6 h-6" /> : "Reset Password"}
          </motion.button>

          {/* Back to login */}
          <div className="text-center text-sm text-neutral-400 mt-4">
            <a
              href="/login"
              className="text-primary-light font-semibold hover:underline"
            >
              ⬅ Back to login
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
