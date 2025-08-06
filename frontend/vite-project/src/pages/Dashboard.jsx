import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FaPlus, FaPowerOff, FaStop, FaRedo, FaTrashAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import LoadingSpinner from '../components/LoadingSpinner';
import * as containerService from '../services/containerService';
import { toast } from 'react-toastify';

// Composant IconButton réutilisable
function IconButton({ icon, onClick, color, hover, title }) {
    return (
        <button
            onClick={onClick}
            className={`p-3 text-white rounded-full shadow-md transition-all transform hover:scale-110 ${color} ${hover}`}
            title={title}
            aria-label={title}
        >
            {icon}
        </button>
    );
}

export default function Dashboard() {
    const navigate = useNavigate();
    const [containers, setContainers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchContainers();
    }, []);

    const fetchContainers = async () => {
        try {
            const response = await containerService.getContainers();
            setContainers(response.containers || []);
        } catch (error) {
            toast.error(error.message || 'Erreur lors du chargement des conteneurs.');
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (containerId, action) => {
        try {
            await containerService.performAction(containerId, action);
            toast.success(`Action "${action}" réussie.`);
            fetchContainers();
        } catch (error) {
            toast.error(error.message || `Échec de l'action "${action}".`);
        }
    };

    return (
        <div className="flex min-h-screen bg-background font-sans text-text">
            <Sidebar />
            <main className="flex-1 p-10">
                <header className="flex justify-between items-center mb-10 border-b pb-4">
                    <h1 className="text-4xl font-bold text-text">Tableau de bord</h1>
                    <button
                        onClick={() => navigate('/create-container')}
                        className="flex items-center gap-2 px-5 py-3 bg-primary text-white rounded-xl shadow-md hover:bg-primary-dark transition-all duration-300 hover:scale-105"
                    >
                        <FaPlus /> Nouveau conteneur
                    </button>
                </header>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <LoadingSpinner size="w-12 h-12" color="text-primary" />
                    </div>
                ) : (
                    <motion.section
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.4 }}
                        className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                    >
                        {containers.length > 0 ? (
                            containers.map((container) => (
                                <motion.div
                                    key={container.id}
                                    className="bg-card p-6 rounded-2xl shadow-xl border border-gray-100 hover:shadow-2xl transition-shadow duration-300"
                                    whileHover={{ y: -4 }}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <h2 className="text-xl font-semibold">{container.name}</h2>
                                        <span
                                            className={`px-3 py-1 text-xs font-semibold rounded-full ${
                                                container.status === 'running'
                                                    ? 'bg-accent text-white'
                                                    : 'bg-secondary-light text-secondary-dark'
                                            }`}
                                        >
                                            {container.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-secondary">{container.image}</p>

                                    <div className="flex justify-start gap-3 mt-6">
                                        <IconButton
                                            icon={<FaPowerOff />}
                                            onClick={() => handleAction(container.id, 'start')}
                                            color="bg-accent"
                                            hover="hover:bg-green-600"
                                            title="Démarrer"
                                        />
                                        <IconButton
                                            icon={<FaStop />}
                                            onClick={() => handleAction(container.id, 'stop')}
                                            color="bg-yellow-500"
                                            hover="hover:bg-yellow-600"
                                            title="Arrêter"
                                        />
                                        <IconButton
                                            icon={<FaRedo />}
                                            onClick={() => handleAction(container.id, 'restart')}
                                            color="bg-primary"
                                            hover="hover:bg-primary-dark"
                                            title="Redémarrer"
                                        />
                                        <IconButton
                                            icon={<FaTrashAlt />}
                                            onClick={() => handleAction(container.id, 'remove')}
                                            color="bg-red-500"
                                            hover="hover:bg-red-600"
                                            title="Supprimer"
                                        />
                                    </div>
                                </motion.div>
                            ))
                        ) : (
                            <div className="col-span-full text-center py-12 bg-card rounded-xl shadow-md text-secondary">
                                Aucun conteneur trouvé. Déployez votre premier.
                            </div>
                        )}
                    </motion.section>
                )}
            </main>
        </div>
    );
}