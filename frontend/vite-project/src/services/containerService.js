import api from './api';

export const getContainers = async () => {
    try {
        const response = await api.get('/containers');
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const createContainer = async (containerData) => {
    try {
        const response = await api.post('/containers', containerData);
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const performAction = async (containerId, action) => {
    try {
        const response = await api.post(`/containers/${containerId}/${action}`);
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};