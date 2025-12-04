// src/App.jsx
import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { initializeTheme, toggleDarkMode } from './theme';

// Import Pages
import CreateContainerPage from './pages/CreateContainerPage';
import Dashboard from './pages/Dashboard';
import ForgotPassword from './pages/ForgotPassword';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import ResetPassword from './pages/ResetPassword';
import Settings from './pages/Settings';
import Signup from './pages/Signup';

export default function App() {
  useEffect(() => {
    initializeTheme();
  }, []);

  return (
    <AuthProvider>
      {/* Railway-style background */}
      <div className="page-bg min-h-screen text-text">
        {/*  Theme Toggle */}
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={toggleDarkMode}
            className="btn-ghost bg-card/50 hover:bg-card/80 text-text-light font-medium shadow-card transition duration-200"
          >
            Toggle Theme
          </button>
        </div>

        {/*  Main Routes */}
        <div className="min-h-screen thin-scrollbar">
          <Routes>
            {/* Redirect root to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />

            {/* Authenticated Routes */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/create-container" element={<CreateContainerPage />} />
            <Route path="/settings" element={<Settings />} />

            {/* Fallback */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>

        {/* Toast notifications */}
        <ToastContainer theme="dark" position="bottom-right" />
      </div>
    </AuthProvider>
  );
}
