// src/App.jsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import SplashScreen from "./components/SplashScreen";
import HomePage from "./components/HomePage";
import PanelPage from "./components/PanelPage.jsx";
import EditPanelPage from "./components/EditPanelPage.jsx";

function App() {
    return (
        <Routes>
            <Route path="/" element={<SplashScreen />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/panels" element={<PanelPage />} />
            <Route path="/edit-panel/:panelNumber" element={<EditPanelPage />} />
        </Routes>
    );
}

export default App;