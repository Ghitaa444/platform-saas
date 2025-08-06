import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import { FaUserEdit, FaLock } from 'react-icons/fa';

export default function Settings() {
    const [activeTab, setActiveTab] = useState('profile');

    const renderContent = () => {
        if (activeTab === 'profile') {
            return (
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-card p-8 rounded-xl shadow-lg"
                >
                    <h2 className="text-2xl font-bold text-text mb-6">Profil</h2>
                    <form className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-secondary">Nom d'utilisateur</label>
                            <input
                                type="text"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                                placeholder="Votre nom"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary">Adresse e-mail</label>
                            <input
                                type="email"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                                placeholder="Votre e-mail"
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition duration-300"
                        >
                            Enregistrer les modifications
                        </button>
                    </form>
                </motion.div>
            );
        } else if (activeTab === 'security') {
            return (
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-card p-8 rounded-xl shadow-lg"
                >
                    <h2 className="text-2xl font-bold text-text mb-6">Sécurité</h2>
                    <form className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-secondary">Ancien mot de passe</label>
                            <input
                                type="password"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary">Nouveau mot de passe</label>
                            <input
                                type="password"
                                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition duration-300"
                        >
                            Changer le mot de passe
                        </button>
                    </form>
                </motion.div>
            );
        }
    };

    return (
        <div className="flex bg-background min-h-screen font-sans text-text">
            <Sidebar />
            <div className="flex-1 p-8">
                <div className="flex justify-between items-center mb-8 pb-4 border-b border-gray-200">
                    <h1 className="text-4xl font-extrabold text-text">Paramètres</h1>
                </div>

                <div className="flex flex-col md:flex-row gap-8">
                    <div className="w-full md:w-1/4">
                        <nav className="flex flex-col space-y-2 bg-card p-4 rounded-xl shadow-md">
                            <button
                                onClick={() => setActiveTab('profile')}
                                className={`flex items-center px-4 py-2 rounded-md transition duration-300 ${activeTab === 'profile' ? 'bg-primary text-white shadow-sm' : 'text-secondary hover:bg-gray-100'}`}
                            >
                                <FaUserEdit className="mr-2" />
                                Profil
                            </button>
                            <button
                                onClick={() => setActiveTab('security')}
                                className={`flex items-center px-4 py-2 rounded-md transition duration-300 ${activeTab === 'security' ? 'bg-primary text-white shadow-sm' : 'text-secondary hover:bg-gray-100'}`}
                            >
                                <FaLock className="mr-2" />
                                Sécurité
                            </button>
                        </nav>
                    </div>
                    <div className="flex-1">
                        {renderContent()}
                    </div>
                </div>
            </div>
        </div>
    );
}