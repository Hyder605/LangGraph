// src/context/MangaContext.jsx
import React, { createContext, useState, useContext } from 'react';

// Create the Context
const MangaContext = createContext();

// Create the Provider Component
export const MangaProvider = ({ children }) => {
    const [mangaData, setMangaData] = useState({
        sessionId: null,
        panels: [],
        story: ""
    });

    const updateMangaData = (newData) => {
        setMangaData(prev => ({ ...prev, ...newData }));
    };

    const updatePanelImage = (panelIndex, newImagePath, newPrompt = null) => {
        setMangaData(prev => {
            const newPanels = [...prev.panels];
            if (newPanels[panelIndex]) {
                newPanels[panelIndex] = {
                    ...newPanels[panelIndex],
                    image_path: newImagePath,
                    image_prompt: newPrompt !== null ? newPrompt : newPanels[panelIndex].image_prompt
                };
            }
            return { ...prev, panels: newPanels };
        });
    };

    return (
        <MangaContext.Provider value={{ mangaData, updateMangaData, updatePanelImage }}>
            {children}
        </MangaContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useMangaContext = () => useContext(MangaContext);