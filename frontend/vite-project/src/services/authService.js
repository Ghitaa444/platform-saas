import api from './api';

// 🔐 Connexion
export const login = async ({ username, password }) => {
  const response = await api.post('/api/auth/login', { username, password });
  return response.data;
};

// 🆕 Inscription
export const signup = async ({ username, email, password }) => {
  const response = await api.post('/api/auth/register', { username, email, password });
  return response.data;
};

// 📩 Mot de passe oublié
export const forgotPassword = async (email) => {
  const response = await api.post('/api/auth/forgot-password', { email });
  return response.data;
};

// 🔁 Réinitialisation du mot de passe
export const resetPassword = async ({ token, new_password }) => {
  const response = await api.post('/api/auth/reset-password', { token, new_password });
  return response.data;
};
