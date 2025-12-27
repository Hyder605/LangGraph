// src/components/PanelPage.jsx
import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useMangaContext } from "../context/MangaContext";

import html2canvas from "html2canvas";

function PanelPage() {
    const navigate = useNavigate();

    // 1. Get Data from Context (Single Source of Truth)
    const { mangaData } = useMangaContext();
    const { panels, sessionId } = mangaData;

    // 2. Local State
    const [hoveredPanel, setHoveredPanel] = useState(null);
    const [isExporting, setIsExporting] = useState(false); // PDF loading state

    // 3. Fallback logic
    const panelList = panels && panels.length > 0 ? panels : [];

    // 4. REF for PDF Capture
    const mangaGridRef = useRef(null);

    const handlePanelClick = (index) => {
        navigate(`/edit-panel/${index + 1}`);
    };

    // -------------------------------------------------------------------------
    // EXPORT PNG FUNCTION
    // -------------------------------------------------------------------------
    const handleExportPNG = async () => {
        if (!mangaGridRef.current) return;
        setIsExporting(true);

        try {
            const element = mangaGridRef.current;

            // 1. Temporarily remove max-height so it expands to full natural size
            const originalMaxHeight = element.style.maxHeight;
            const originalOverflow = element.style.overflow;

            element.style.maxHeight = "none";
            element.style.overflow = "visible";

            // 2. Capture
            const canvas = await html2canvas(element, {
                scale: 3,
                useCORS: true,
                backgroundColor: "#ffffff",
                logging: false,
                // These ensure we capture the full natural dimensions
                width: element.offsetWidth,
                height: element.offsetHeight,
                scrollY: -window.scrollY // Corrects for window scrolling issues
            });

            // 3. Restore original styles immediately
            element.style.maxHeight = originalMaxHeight;
            element.style.overflow = originalOverflow;

            // 4. Download
            const imageUrl = canvas.toDataURL("image/png", 1.0);
            const link = document.createElement("a");
            link.href = imageUrl;
            const shortId = sessionId ? sessionId.slice(0, 8) : "manga";
            link.download = `manga-export-${shortId}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } catch (error) {
            console.error("PNG Export failed:", error);
            alert("Failed to export.");
        } finally {
            setIsExporting(false);
        }
    };



    // -------------------------------------------------------------------------
    // DYNAMIC GRID LAYOUT GENERATOR
    // -------------------------------------------------------------------------
    const getGridStyle = (index, total) => {
        const base = {
            position: "relative",
            overflow: "hidden",
            cursor: "pointer",
            backgroundColor: "#222",
            border: "1px solid rgba(255,255,255,0.1)"
        };

        if (total === 4) {
            return { ...base, gridColumn: "span 3", gridRow: "span 1" };
        }

        if (total === 5) {
            if (index < 2) return { ...base, gridColumn: "span 3", gridRow: "1" };
            else return { ...base, gridColumn: "span 2", gridRow: "2" };
        }

        return {
            ...base,
            gridColumn: `span ${Math.floor(6 / Math.ceil(Math.sqrt(total)))}`,
            minHeight: "100%"
        };
    };

    const getContainerGridTemplate = (count) => {
        if (count === 4) return { rows: "1fr 1fr", cols: "repeat(6, 1fr)" };
        if (count === 5) return { rows: "1fr 1fr", cols: "repeat(6, 1fr)" };
        if (count <= 2) return { rows: "1fr", cols: `repeat(${count}, 1fr)` };
        return { rows: "repeat(auto-fit, minmax(200px, 1fr))", cols: "repeat(6, 1fr)" };
    };

    const gridConfig = getContainerGridTemplate(panelList.length);

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

    const getPanelOverlayStyle = (index) => ({
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        background: "rgba(0, 0, 0, 0.6)",
        backdropFilter: hoveredPanel === index ? "blur(4px)" : "none",
        WebkitBackdropFilter: hoveredPanel === index ? "blur(4px)" : "none",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: hoveredPanel === index ? 1 : 0,
        transition: "opacity 0.2s ease, backdrop-filter 0.2s ease",
        pointerEvents: hoveredPanel === index ? "auto" : "none",
    });

    return (
        <div className="position-relative w-100" style={bgStyle}>
            <div className="position-absolute top-0 start-0 w-100 h-100" style={overlayStyle}/>

            <div className="position-relative d-flex flex-column" style={{ minHeight: "100vh" }}>

                <header className="container d-flex justify-content-between align-items-center pt-4 pb-3">
                    <div className="d-flex gap-3" style={{ alignItems: "flex-start" }}>
                        <button onClick={() => navigate('/home')} style={{ color: "white", background: "none", border: "none", padding: 0, cursor: "pointer", fontSize: "40px", lineHeight: 0.5 }}>‹</button>
                        <div>
                            <h5 className="text-white fw-semibold mb-1">Your Manga</h5>
                            <p className="text-white-50 mb-0 small">Generated {panelList.length} panels</p>
                        </div>
                    </div>
                    <button
                        className="btn btn-light btn-sm px-3 py-2 fw-semibold rounded-2"
                        onClick={handleExportPNG}
                        disabled={isExporting}
                    >
                        {isExporting ? "Saving..." : "Export as PNG"}
                    </button>

                </header>

                <main className="container flex-grow-1 d-flex pb-4">
                    {/* ATTACH REF HERE FOR PDF CAPTURE */}
                    <div
                        ref={mangaGridRef}
                        className="bg-white rounded-2 shadow-lg p-2 w-100"
                        style={{ maxHeight: "calc(100vh - 140px)" }}
                    >

                        {/* DYNAMIC GRID CONTAINER */}
                        <div style={{
                            display: "grid",
                            gridTemplateRows: gridConfig.rows,
                            gridTemplateColumns: gridConfig.cols,
                            gap: "8px",
                            height: "100%",
                        }}>

                            {/* DYNAMICALLY MAP PANELS */}
                            {panelList.map((panel, index) => (
                                <div
                                    key={index}
                                    style={getGridStyle(index, panelList.length)}
                                    onMouseEnter={() => setHoveredPanel(index)}
                                    onMouseLeave={() => setHoveredPanel(null)}
                                    onClick={() => handlePanelClick(index)}
                                >
                                    <img
                                        src={panel.image_path || "/panels/luffy_bg.png"}
                                        alt={`Panel ${index + 1}`}
                                        crossOrigin="anonymous" // IMPORTANT FOR CORS
                                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                                        onError={(e) => { e.target.src = "/panels/luffy_bg.png"; }}
                                    />
                                    <div style={getPanelOverlayStyle(index)}>
                                        <button className="btn btn-light btn-sm px-4 fw-semibold">
                                            Edit
                                        </button>
                                    </div>

                                    <div className="position-absolute bottom-0 end-0 m-2 badge bg-dark opacity-75">
                                        #{index + 1}
                                    </div>
                                </div>
                            ))}

                            {/* EMPTY STATE */}
                            {panelList.length === 0 && (
                                <div style={{ gridColumn: "1 / -1", display: "flex", alignItems: "center", justifyContent: "center", color: "#888" }}>
                                    No panels found. Please try generating again.
                                </div>
                            )}

                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default PanelPage;
