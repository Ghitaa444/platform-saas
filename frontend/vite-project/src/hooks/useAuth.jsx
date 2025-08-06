import React, { createContext, useContext, useState, useEffect } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Here you would check for a stored token or session to automatically log the user in
        const token = localStorage.getItem('authToken');
        if (token) {
            // A simplified check. In a real app, you'd validate the token with the backend.
            setUser({ name: 'User' });
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const response = await authService.login({ email, password });
            localStorage.setItem('authToken', response.token);
            setUser({ name: response.user.name });
            setLoading(false);
        } catch (error) {
            setLoading(false);
            throw error;
        }
    };

    const signup = async (name, email, password) => {
        setLoading(true);
        try {
            const response = await authService.signup({ name, email, password });
            localStorage.setItem('authToken', response.token);
            setUser({ name: response.user.name });
            setLoading(false);
        } catch (error) {
            setLoading(false);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        setUser(null);
    };

    const value = {
        user,
        loading,
        login,
        signup,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    return useContext(AuthContext);
};