// src/components/EditPanelPage.jsx
import React, { useRef, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMangaContext } from "../context/MangaContext";
import { mangaService } from "../services/mangaService"; // Import service

function EditPanelPage() {
    const { panelNumber } = useParams();
    const navigate = useNavigate();

    // 1. DATA FROM CONTEXT
    const { mangaData, updatePanelImage } = useMangaContext();
    const { panels, sessionId } = mangaData;

    // 2. CURRENT PANEL DATA
    const panelIndex = parseInt(panelNumber) - 1;
    const panelData = panels && panels[panelIndex] ? panels[panelIndex] : null;

    // 3. UI STATE
    const [sceneDescription, setSceneDescription] = useState(
        panelData ? (panelData.image_prompt || "No description available.") : "Loading..."
    );

    const initialImage = panelData ? (panelData.image_path || "/panels/luffy_bg.png") : "/panels/luffy_bg.png";
    const [currentPanelImage, setCurrentPanelImage] = useState(initialImage);

    // Variations List
    const [variations, setVariations] = useState([
        { id: Date.now(), image: initialImage, label: "Original" }
    ]);

    // Select the first one initially
    const [selectedLayout, setSelectedLayout] = useState(variations[0].id);

    const [refinements, setRefinements] = useState("");
    const [isRegenerating, setIsRegenerating] = useState(false);

    const sceneRef = useRef(null);
    const refinementsRef = useRef(null);

    // Auto-resize
    useEffect(() => {
        const adjust = (el) => {
            if (!el) return;
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight, 180) + "px";
        };
        adjust(sceneRef.current);
        adjust(refinementsRef.current);
    }, [sceneDescription, refinements]);

    // -------------------------------------------------------------------------
    // API: REGENERATE PANEL
    // -------------------------------------------------------------------------
    const handleRegenerate = async () => {
        if (!sessionId) {
            alert("Session ID is missing. Cannot regenerate.");
            return;
        }
        setIsRegenerating(true);

        try {
            // 1. Prepare Payload
            const payload = {
                session_id: sessionId,
                panel_number: parseInt(panelNumber),
                prompt: sceneDescription,
                refinements: refinements
            };

            console.log("Regenerating with payload:", payload);

            // 2. Call API
            const result = await mangaService.regeneratePanel(payload);
            console.log("Regeneration result:", result);

            // 3. Fix Image URL (Prepend Backend URL if relative)
            let newImageUrl = result.image_path;

            // TODO: Ensure this matches your actual backend address
            const API_BASE_URL = "http://203.241.246.178:8000";

            if (newImageUrl && newImageUrl.startsWith("/")) {
                newImageUrl = `${API_BASE_URL}${newImageUrl}`;
            }

            if (!newImageUrl) {
                throw new Error("Invalid image path received from API");
            }

            // 4. Create Variation Object
            // Logic: length 1 -> 'A', length 2 -> 'B'
            const nextChar = String.fromCharCode(65 + (variations.length - 1));
            const newVariation = {
                id: Date.now(),
                image: newImageUrl,
                label: `Variation ${nextChar}`
            };

            // 5. Add to List (BUT DO NOT AUTO-SELECT)
            setVariations(prev => [...prev, newVariation]);

            // Clear input
            setRefinements("");

        } catch (error) {
            console.error("Regeneration failed:", error);
            alert("Failed to regenerate panel. Check console.");
        } finally {
            setIsRegenerating(false);
        }
    };

    // -------------------------------------------------------------------------
    // DYNAMIC DIMENSION LOGIC
    // -------------------------------------------------------------------------
    const getPanelDimensions = () => {
        const panelNum = parseInt(panelNumber);
        const totalPanels = panels ? panels.length : 5;

        if (totalPanels === 4) return { width: "500px", height: "350px" };
        if (totalPanels === 5) {
            return panelNum <= 2
                ? { width: "600px", height: "350px" }
                : { width: "400px", height: "350px" };
        }
        return { width: "500px", height: "350px" };
    };

    const panelDimensions = getPanelDimensions();

    const handleLayoutSelect = (layoutId, imageSource) => {
        setSelectedLayout(layoutId);
        setCurrentPanelImage(imageSource);
    };


    const handleBack = () => {
        // SAVE logic: Update the global state with whatever image is currently selected/viewed
        if (updatePanelImage && currentPanelImage) {
            updatePanelImage(panelIndex, currentPanelImage, sceneDescription);
        }

        navigate('/panels');
    };

    // -------------------------------------------------------------------------
    // STYLES
    // -------------------------------------------------------------------------
    const bgStyle = {
        backgroundImage: "url('/luffy_bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#000",
        minHeight: "100vh",
    };
    const overlayStyle = {
        background: "linear-gradient(135deg, rgba(0, 0, 0, 0.75), rgba(10, 10, 10, 0.55))",
        backdropFilter: "blur(3px)",
        WebkitBackdropFilter: "blur(3px)",
    };

    return (
        <div className="position-relative w-100" style={bgStyle}>
            <div className="position-absolute top-0 start-0 w-100 h-100" style={overlayStyle}/>

            <div className="position-relative d-flex flex-column" style={{ minHeight: "100vh" }}>
                <header className="container d-flex justify-content-between align-items-center pt-4 pb-3">
                    <div className="d-flex gap-3" style={{ alignItems: "flex-start" }}>
                        <button onClick={handleBack} style={{ color: "white", background: "none", border: "none", padding: 0, cursor: "pointer", fontSize: "40px", lineHeight: 0.5 }}>‹</button>
                        <div>
                            <h5 className="text-white fw-semibold mb-1">Editing Panel {panelNumber}</h5>
                            <p className="text-white-50 mb-0 small">Choose your favorite or regenerate</p>
                        </div>
                    </div>
                    <button className="btn btn-light btn-sm px-3 py-2 fw-semibold rounded-2" onClick={handleBack}>
                        Save & Back
                    </button>
                </header>

                <main className="container flex-grow-1 d-flex flex-column pb-4">
                    {/* Top Section */}
                    <div style={{ display: "flex", gap: "16px", marginBottom: "24px", alignItems: "start", flexWrap: "wrap" }}>
                        <div style={{ flex: "0 0 auto" }}>
                            <div className="text-white small fw-semibold mb-2">Current Version</div>
                            <div className="bg-white rounded-2 shadow-lg overflow-hidden" style={{ width: panelDimensions.width, height: panelDimensions.height }}>
                                <img src={currentPanelImage} alt={`Panel ${panelNumber}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} onError={(e) => { e.target.src = "/panels/luffy_bg.png"; }} />
                            </div>
                        </div>
                        <div style={{ flex: "1 1 300px", minWidth: "300px" }}>
                            <div className="text-white small fw-semibold mb-2">Scene Description</div>
                            <div className="rounded-2 p-3" style={{ backgroundColor: "rgba(0, 0, 0, 0.20)", backdropFilter: "blur(3px)", height: panelDimensions.height }}>
                                <textarea ref={sceneRef} className="form-control border-0 bg-transparent text-white" value={sceneDescription} onChange={(e) => setSceneDescription(e.target.value)} style={{ height: "100%", resize: "none", boxShadow: "none", outline: "none", overflowY: "auto" }} />
                            </div>
                        </div>
                    </div>

                    {/* Refinements */}
                    <div className="mb-3">
                        <div className="text-white small fw-semibold mb-2">Refinements <span className="text-white-50">(optional)</span></div>
                        <div className="rounded-2 p-3" style={{ backgroundColor: "rgba(0, 0, 0, 0.20)", backdropFilter: "blur(3px)" }}>
                            <textarea ref={refinementsRef} className="form-control border-0 bg-transparent text-white" rows={2} value={refinements} onChange={(e) => setRefinements(e.target.value)} placeholder="e.g., more dramatic lighting, change character pose..." style={{ minHeight: "60px", maxHeight: "100px", resize: "none", boxShadow: "none", outline: "none" }} />
                        </div>
                    </div>

                    {/* Regenerate Button */}
                    <button className="btn btn-light rounded-2 fw-semibold py-3 mb-4" onClick={handleRegenerate} disabled={isRegenerating}>
                        {isRegenerating ? (
                            <span><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Regenerating...</span>
                        ) : ( "✦ Regenerate This Panel" )}
                    </button>

                    {/* Dynamic Versions List */}
                    <div className="text-white small fw-semibold mb-2">Versions ({variations.length})</div>
                    <div style={{ display: "grid", gridTemplateColumns: `repeat(auto-fit, ${panelDimensions.width})`, gap: "16px", justifyContent: "start" }}>
                        {variations.map((layout) => (
                            <div key={layout.id} style={{ position: "relative" }}>
                                <div className="bg-white rounded-2 shadow-lg overflow-hidden"
                                     style={{ width: panelDimensions.width, height: panelDimensions.height, cursor: "pointer", border: selectedLayout === layout.id ? "3px solid #0d6efd" : "3px solid transparent", transition: "border 0.2s ease" }}
                                     onClick={() => handleLayoutSelect(layout.id, layout.image)}>
                                    <img src={layout.image} alt={layout.label} style={{ width: "100%", height: "100%", objectFit: "cover" }} onError={(e) => { e.target.src = "/panels/luffy_bg.png"; }} />
                                </div>
                                <div className="d-flex align-items-center mt-2" style={{ cursor: "pointer" }} onClick={() => handleLayoutSelect(layout.id, layout.image)}>
                                    <input type="radio" checked={selectedLayout === layout.id} readOnly style={{ width: "20px", height: "20px", accentColor: "#0d6efd" }} />
                                    <label className="text-white ms-2 mb-0" style={{ cursor: "pointer" }}>{layout.label}</label>
                                </div>
                            </div>
                        ))}
                    </div>
                </main>
                <footer className="mt-auto text-center text-white-50 small mb-3 mt-4">Generate more versions to compare different styles</footer>
            </div>
        </div>
    );
}

export default EditPanelPage;
