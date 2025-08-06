import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function NotFound() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-center px-4">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <h1 className="text-9xl font-extrabold text-blue-600">404</h1>
                <p className="text-2xl font-bold text-gray-800 mt-4">Page non trouvée</p>
                <p className="text-gray-500 mt-2">Désolé, la page que vous recherchez n'existe pas.</p>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="mt-8 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                    Retour au tableau de bord
                </button>
            </motion.div>
        </div>
    );
}