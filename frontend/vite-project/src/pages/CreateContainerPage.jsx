import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaPlus, FaArrowLeft, FaTrashAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';
import * as containerService from '../services/containerService';
import LoadingSpinner from '../components/LoadingSpinner';

export default function CreateContainerPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        image_name: '',
        container_name: '',
        ports: [''],
        environment: '',
        network: '',
        volumes: [''],
        cpu_shares: 1024,
        memory: '1g',
    });
    const [isCreating, setIsCreating] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handlePortChange = (index, e) => {
        const newPorts = [...formData.ports];
        newPorts[index] = e.target.value;
        setFormData(prev => ({ ...prev, ports: newPorts }));
    };

    const addPort = () => {
        setFormData(prev => ({ ...prev, ports: [...prev.ports, ''] }));
    };

    const removePort = (index) => {
        const newPorts = formData.ports.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, ports: newPorts }));
    };

    const handleVolumeChange = (index, e) => {
        const newVolumes = [...formData.volumes];
        newVolumes[index] = e.target.value;
        setFormData(prev => ({ ...prev, volumes: newVolumes }));
    };

    const addVolume = () => {
        setFormData(prev => ({ ...prev, volumes: [...prev.volumes, ''] }));
    };

    const removeVolume = (index) => {
        const newVolumes = formData.volumes.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, volumes: newVolumes }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsCreating(true);

        try {
            if (!formData.image_name || !formData.container_name) {
                toast.error("Le nom de l'image et du conteneur sont requis.");
                return;
            }

            const response = await containerService.createContainer({
                image_name: formData.image_name,
                container_name: formData.container_name,
                ports: formData.ports.filter(p => p.trim() !== ''),
                environment: formData.environment,
                network: formData.network,
                volumes: formData.volumes.filter(v => v.trim() !== ''),
                cpu_shares: formData.cpu_shares,
                memory: formData.memory,
            });

            if (response && response.container) {
                toast.success(`Conteneur '${response.container.name}' créé avec succès !`);
                navigate('/dashboard');
            } else {
                toast.error("Erreur inattendue lors de la création du conteneur.");
            }
        } catch (error) {
            console.error("Erreur lors de la création du conteneur:", error);
            const errorMessage = error.data?.message || error.message || "Échec de la création du conteneur.";
            toast.error(errorMessage);
        } finally {
            setIsCreating(false);
        }
    };

    const FormSection = ({ title, children }) => (
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">{title}</h2>
            {children}
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="max-w-6xl w-full mx-auto bg-white p-10 rounded-xl shadow-2xl"
            >
                <div className="flex justify-between items-center mb-8 pb-4 border-b border-gray-200">
                    <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
                        Déployer un conteneur
                    </h1>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center text-blue-600 hover:text-blue-800 transition duration-300"
                    >
                        <FaArrowLeft className="mr-2" /> Retour au tableau de bord
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* Basic Settings Section */}
                    <FormSection title="Informations de base">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="image_name" className="block text-sm font-medium text-gray-700 mb-2">
                                    Nom de l'image <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    id="image_name"
                                    name="image_name"
                                    value={formData.image_name}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300"
                                    placeholder="Ex: nginx:latest, postgres:14"
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="container_name" className="block text-sm font-medium text-gray-700 mb-2">
                                    Nom du conteneur <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    id="container_name"
                                    name="container_name"
                                    value={formData.container_name}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300"
                                    placeholder="Ex: mon-serveur-web"
                                    required
                                />
                            </div>
                        </div>
                    </FormSection>

                    {/* Port Mappings Section */}
                    <FormSection title="Mappage de ports">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ports <span className="text-gray-500 font-normal text-xs">(Ex: 8080:80)</span>
                        </label>
                        {formData.ports.map((port, index) => (
                            <div key={index} className="flex items-center gap-2 mb-2">
                                <input
                                    type="text"
                                    value={port}
                                    onChange={(e) => handlePortChange(index, e)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300"
                                    placeholder="HOST_PORT:CONTAINER_PORT"
                                />
                                {formData.ports.length > 1 && (
                                    <motion.button
                                        type="button"
                                        onClick={() => removePort(index)}
                                        className="p-3 text-red-500 hover:text-red-700 transition duration-300"
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                    >
                                        <FaTrashAlt />
                                    </motion.button>
                                )}
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={addPort}
                            className="mt-4 flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition duration-300"
                        >
                            <FaPlus className="mr-2" /> Ajouter un port
                        </button>
                    </FormSection>

                    {/* Volumes Section */}
                    <FormSection title="Volumes">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Volumes <span className="text-gray-500 font-normal text-xs">(Ex: /host/path:/container/path)</span>
                        </label>
                        {formData.volumes.map((volume, index) => (
                            <div key={index} className="flex items-center gap-2 mb-2">
                                <input
                                    type="text"
                                    value={volume}
                                    onChange={(e) => handleVolumeChange(index, e)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300"
                                    placeholder="HOST_PATH:CONTAINER_PATH"
                                />
                                {formData.volumes.length > 1 && (
                                    <motion.button
                                        type="button"
                                        onClick={() => removeVolume(index)}
                                        className="p-3 text-red-500 hover:text-red-700 transition duration-300"
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                    >
                                        <FaTrashAlt />
                                    </motion.button>
                                )}
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={addVolume}
                            className="mt-4 flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition duration-300"
                        >
                            <FaPlus className="mr-2" /> Ajouter un volume
                        </button>
                    </FormSection>

                    {/* Submit button */}
                    <div className="mt-8">
                        <motion.button
                            type="submit"
                            className="w-full flex justify-center items-center px-6 py-4 bg-blue-600 text-white rounded-lg font-bold text-xl hover:bg-blue-700 transition duration-300 shadow-md"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isCreating}
                        >
                            {isCreating ? (
                                <LoadingSpinner size="w-6 h-6" color="text-white" />
                            ) : (
                                <>
                                    <FaPlus className="mr-3" />
                                    Créer le conteneur
                                </>
                            )}
                        </motion.button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
}