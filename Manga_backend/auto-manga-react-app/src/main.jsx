import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // <--- 1. Import this
import App from './App.jsx'; // Make sure extension is correct
import { MangaProvider } from './context/MangaContext';
import 'bootstrap/dist/css/bootstrap.min.css';

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <BrowserRouter>
            <MangaProvider>
                <App />
            </MangaProvider>
        </BrowserRouter>
    </React.StrictMode>
);
