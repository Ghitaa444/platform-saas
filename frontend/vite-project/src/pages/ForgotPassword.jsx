import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { forgotPassword } from "../services/authService";
import LoadingSpinner from "../components/LoadingSpinner";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await forgotPassword(email);
      toast.success("Un lien de réinitialisation a été envoyé à votre e-mail");
      navigate("/login");
    } catch (error) {
      if (error.response?.status === 404) {
        toast.info("La fonctionnalité de réinitialisation n’est pas encore activée ");
      } else {
        toast.error(error?.msg || error?.message || "Une erreur est survenue ");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 relative overflow-hidden text-gray-100">
      {/* 🔵 Dégradés lumineux animés */}
      <motion.div
        className="absolute w-80 h-80 bg-blue-600/30 rounded-full blur-[120px] top-10 left-16"
        animate={{ x: [0, 50, 0], y: [0, 40, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-[420px] h-[420px] bg-indigo-500/25 rounded-full blur-[140px] bottom-10 right-10"
        animate={{ x: [0, -60, 0], y: [0, -40, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* 💠 Carte centrale */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md bg-gray-900/70 backdrop-blur-2xl border border-gray-800 rounded-2xl shadow-2xl p-10"
      >
        {/* 🌀 Branding */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-500 via-indigo-400 to-purple-500 text-transparent bg-clip-text">
            Dockly
          </h1>
          <p className="text-gray-400 mt-1 text-sm">Plateforme Cloud pour Conteneurs 🚀</p>
        </motion.div>

        {/*  Titre principal */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-100">
            Mot de passe oublié ?
          </h2>
          <p className="text-gray-400 text-sm mt-2">
            Entrez votre adresse e-mail pour recevoir un lien sécurisé 
          </p>
        </div>

        {/*  Formulaire */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Adresse e-mail
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="exemple@email.com"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-800/70 border border-gray-700 text-gray-100 placeholder-gray-500 
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
          </div>

          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.97 }}
            className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500 
                       text-white font-semibold shadow-lg hover:shadow-blue-500/20 
                       transition-transform transform hover:scale-[1.02] focus:ring-4 focus:ring-blue-500/30"
          >
            {loading ? <LoadingSpinner size="w-6 h-6" /> : "Envoyer le lien"}
          </motion.button>

          {/* Lien retour */}
          <div className="text-center text-sm text-gray-500 mt-4">
            <a
              href="/login"
              className="text-blue-400 font-medium hover:underline hover:text-blue-300 transition"
            >
              ⬅ Retour à la connexion
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
