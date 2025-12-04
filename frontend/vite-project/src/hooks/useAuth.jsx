import React, { createContext, useContext, useState, useEffect } from 'react';
import * as authService from '../services/authService';
import { jwtDecode } from 'jwt-decode';
 // npm install jwt-decode

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Vérifie si un token est déjà stocké (auto-login)
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser({
          username: decoded.sub || decoded.username || 'Utilisateur',
          id: decoded.id || decoded.user_id || 1,
        });
      } catch (error) {
        console.warn('Invalid token detected, removing it');
        localStorage.removeItem('authToken');
      }
    }
    setLoading(false);
  }, []);

  // --- Connexion ---
  const login = async (username, password) => {
    setLoading(true);
    try {
      const response = await authService.login({ username, password });
      const token = response.access_token;
      localStorage.setItem('authToken', token);

      const decoded = jwtDecode(token);
      setUser({
        username: decoded.sub || username,
        id: decoded.id || decoded.user_id,
      });

      return response;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // --- Inscription ---
  const signup = async (username, email, password) => {
    setLoading(true);
    try {
      const response = await authService.signup({ username, email, password });
      const token = response.access_token;
      localStorage.setItem('authToken', token);

      const decoded = jwtDecode(token);
      setUser({
        username: decoded.sub || username,
        id: decoded.id || decoded.user_id,
      });

      return response;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // --- Déconnexion ---
  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
