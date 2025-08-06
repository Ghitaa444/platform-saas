import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import { FaUserEdit, FaLock } from 'react-icons/fa';

export default function Settings() {
    const [activeTab, setActiveTab] = useState('profile');

    const renderContent = () => {
        if (activeTab === 'profile') {
            return (
                <div className="bg-white p-8 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">Profil</h2>
                    <form className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Nom d'utilisateur</label>
                            <input
                                type="text"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md"
                                placeholder="Votre nom"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Adresse e-mail</label>
                            <input
                                type="email"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md"
                                placeholder="Votre e-mail"
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
                        >
                            Enregistrer les modifications
                        </button>
                    </form>
                </div>
            );
        } else if (activeTab === 'security') {
            return (
                <div className="bg-white p-8 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">Sécurité</h2>
                    <form className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Ancien mot de passe</label>
                            <input
                                type="password"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Nouveau mot de passe</label>
                            <input
                                type="password"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md"
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
                        >
                            Changer le mot de passe
                        </button>
                    </form>
                </div>
            );
        }
    };

    return (
        <div className="flex bg-gray-100 min-h-screen">
            <Sidebar />
            <div className="flex-1 p-8">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-extrabold text-gray-900">Paramètres</h1>
                </div>

                <div className="flex flex-col md:flex-row gap-8">
                    <div className="w-full md:w-1/4">
                        <nav className="flex flex-col space-y-2 bg-white p-4 rounded-lg shadow-md">
                            <button
                                onClick={() => setActiveTab('profile')}
                                className={`flex items-center px-4 py-2 rounded-md transition duration-300 ${activeTab === 'profile' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                            >
                                <FaUserEdit className="mr-2" />
                                Profil
                            </button>
                            <button
                                onClick={() => setActiveTab('security')}
                                className={`flex items-center px-4 py-2 rounded-md transition duration-300 ${activeTab === 'security' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                            >
                                <FaLock className="mr-2" />
                                Sécurité
                            </button>
                        </nav>
                    </div>
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                        className="flex-1"
                    >
                        {renderContent()}
                    </motion.div>
                </div>
            </div>
        </div>
    );
}