// src/services/mangaService.js
import apiClient from './api';

export const mangaService = {
    // 1. "Refine with AI" button
    refineStory: async (originalStory, genre) => {
        const response = await apiClient.post('/api/generate', { story: originalStory, genre: genre });

        return response.data;
    },

    // 2. "Create My Manga" button (This one is working fine as JSON)
    createManga: async (payload) => {
        const response = await apiClient.post('/api/approve', payload);
        return response.data;
    },

    regeneratePanel: async (payload) => {
        // payload should be { session_id, panel_number, prompt, refinements }
        const response = await apiClient.post('/api/regenerate-panel', payload);
        return response.data;
    },
};
