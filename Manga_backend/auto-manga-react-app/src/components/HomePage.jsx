// src/components/HomePage.jsx
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
// Import the service to handle API requests
import { mangaService } from "../services/mangaService";
import { useMangaContext } from "../context/MangaContext";

function HomePage() {
    const navigate = useNavigate();
    const { updateMangaData } = useMangaContext();

    // UI States
    const [isLoading, setIsLoading] = useState(false);
    const [isRefining, setIsRefining] = useState(false);
    const [showRefined, setShowRefined] = useState(false);

    // Data States
    const [story, setStory] = useState(
        "A young warrior with spiky black hair discovers an ancient sword in a mystical forest. " +
        "A mysterious hooded figure appears and challenges her to a duel."
    );
    const [refinedText, setRefinedText] = useState("");

    // IMPORTANT: Store the session ID returned by the backend
    const [sessionId, setSessionId] = useState(null);

    // Refs for auto-resizing textareas
    const storyRef = useRef(null);
    const refinedRef = useRef(null);

    // -------------------------------------------------------------------------
    // STEP 1: REFINE STORY (POST /api/generate)
    // -------------------------------------------------------------------------
    const handleRefineClick = async () => {
        if (!story.trim()) return;

        setShowRefined(false); // Hide previous results
        setIsRefining(true);

        try {
            // Call the backend API
            const result = await mangaService.refineStory(story);

            // 1. Store the session ID if present
            if (result.session_id) {
                setSessionId(result.session_id);
                console.log("Session ID captured:", result.session_id);
            }

            // 2. Parse the inner JSON string if necessary
            // The API returns: { generated_story: "{\n \"refined_story\": ... }" }
            let finalRefinedText = "";

            if (typeof result.generated_story === 'string') {
                try {
                    // Try to parse the stringified JSON
                    const parsed = JSON.parse(result.generated_story);
                    finalRefinedText = parsed.refined_story || result.generated_story;
                    // eslint-disable-next-line no-unused-vars
                } catch (e) {
                    // If parsing fails, just use the string as-is
                    finalRefinedText = result.generated_story;
                }
            } else {
                // If it's already an object or undefined
                finalRefinedText = result.generated_story || result;
            }

            setRefinedText(finalRefinedText);
            setShowRefined(true);

            console.log("Refined Story captured:", finalRefinedText);

        } catch (error) {
            console.error("Refine failed:", error);
            alert("Failed to refine the story. Please check the backend connection.");
        } finally {
            setIsRefining(false);
        }
    };

    // -------------------------------------------------------------------------
    // STEP 2: CREATE MANGA (POST /api/approve)
    // -------------------------------------------------------------------------
    const handleCreateClick = async () => {
        // Validation: We need a session ID to proceed
        if (!sessionId) {
            alert("Session ID is missing. Please refine the story first.");
            return;
        }

        setIsLoading(true);


        try {
            const payload = {
                session_id: sessionId,
                edited_story: refinedText || story
            };

            console.log("Payload for /api/approve:", payload);

            const result = await mangaService.createManga(payload);
            console.log("Manga generation success:", result);

            // SAVE TO CONTEXT
            updateMangaData({
                sessionId: result.session_id || sessionId,
                panels: result.prompts,
                story: payload.edited_story
            });

            navigate("/panels", {
                state: {
                    panels: result.prompts, // Changed from result.panels to result.prompts
                    sessionId: result.session_id || sessionId,
                    originalText: payload.edited_story
                }
            });

        } catch (error) {
            console.error("Generation failed:", error);
            alert("Failed to create manga panels. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };


    // -------------------------------------------------------------------------
    // UI HELPER: Auto-resize textareas
    // -------------------------------------------------------------------------
    useEffect(() => {
        const adjust = (el) => {
            if (!el) return;
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight, 180) + "px";
        };

        adjust(storyRef.current);
        adjust(refinedRef.current);
    }, [story, refinedText, showRefined]);


    // -------------------------------------------------------------------------
    // STYLES & RENDER
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
        background:
            "linear-gradient(135deg, rgba(0, 0, 0, 0.55), rgba(10, 10, 10, 0.35))",
        backdropFilter: "blur(2px)",
        WebkitBackdropFilter: "blur(2px)",
    };

    return (
        <div className="position-relative w-100" style={bgStyle}>
            {/* CSS Animations */}
            <style>
                {`
                    @keyframes slideDown {
                        from { opacity: 0; transform: translateY(-20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    
                    @keyframes shimmer {
                        0% { background-position: -1000px 0; }
                        100% { background-position: 1000px 0; }
                    }
                    
                    .refined-section-enter {
                        animation: slideDown 0.5s ease-out forwards;
                    }
                    
                    .refining-shimmer {
                        background: linear-gradient(
                            90deg,
                            rgba(255, 255, 255, 0.1) 0%,
                            rgba(255, 255, 255, 0.3) 50%,
                            rgba(255, 255, 255, 0.1) 100%
                        );
                        background-size: 1000px 100%;
                        animation: shimmer 2s infinite;
                    }
                `}
            </style>

            {/* Dark Glass Overlay */}
            <div
                className="position-absolute top-0 start-0 w-100 h-100"
                style={overlayStyle}
            />

            {/* Main Content */}
            <div
                className="position-relative d-flex flex-column"
                style={{minHeight: "100vh"}}
            >
                {/* TOP: Icon + Title + Subtitle */}
                <header className="pt-4 d-flex flex-column align-items-center text-center mt-4">
                    <div
                        className="d-flex align-items-center justify-content-center bg-white rounded-3 shadow-lg mb-3"
                        style={{width: 70, height: 70}}
                    >
                        <img
                            src="/icons/ai_icon.jpg"
                            alt="Main Icon"
                            className="img-fluid"
                            style={{maxWidth: "70%", maxHeight: "70%"}}
                        />
                    </div>

                    <h2 className="fw-bold text-white mb-1">Auto Manga</h2>
                    <p className="text-white mb-4 fs-6">
                        Turn your story into manga panels with AI
                    </p>
                </header>

                {/* MIDDLE: Story card + button */}
                <main className="container flex-grow-1 d-flex flex-column justify-content-start">
                    <div className="text-white small fw-semibold mb-2">Your story</div>

                    {/* translucent card */}
                    <div
                        className="rounded-2 p-3 mb-3"
                        style={{
                            backgroundColor: "rgba(0, 0, 0, 0.20)",
                            backdropFilter: "blur(3px)",
                            WebkitBackdropFilter: "blur(3px)",
                        }}
                    >
                        <textarea
                            ref={storyRef}
                            className="form-control border-0 bg-transparent text-white"
                            rows={4}
                            value={story}
                            onChange={(e) => setStory(e.target.value)}
                            disabled={isLoading || isRefining}
                            style={{
                                minHeight: "120px",
                                maxHeight: "180px",
                                resize: "none",
                                boxShadow: "none",
                                outline: "none",
                                overflowY: "auto",
                            }}
                        />
                    </div>

                    <button
                        className="btn btn-light rounded-2 fw-semibold py-3"
                        onClick={handleRefineClick}
                        disabled={isLoading || isRefining}
                    >
                        {isRefining ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Refining...
                            </>
                        ) : (
                            "✦ Refine with AI"
                        )}
                    </button>

                    {/* Refining Animation */}
                    {isRefining && (
                        <div className="mt-4">
                            <div className="text-white small fw-semibold mb-2">
                                AI is refining your story...
                            </div>
                            <div
                                className="rounded-2 p-3 refining-shimmer"
                                style={{
                                    backgroundColor: "rgba(0, 0, 0, 0.20)",
                                    backdropFilter: "blur(3px)",
                                    WebkitBackdropFilter: "blur(3px)",
                                    height: "120px",
                                }}
                            >
                            </div>
                        </div>
                    )}

                    {showRefined && (
                        <div className="refined-section-enter">
                            {/* spacer */}
                            <div style={{height: "24px"}}/>

                            {/* Label */}
                            <div className="text-white small fw-semibold mb-2">
                                AI-Refined Prompt
                            </div>

                            {/* Refined prompt box */}
                            <div
                                className="rounded-2 p-3 mb-3"
                                style={{
                                    backgroundColor: "rgba(0, 0, 0, 0.20)",
                                    backdropFilter: "blur(3px)",
                                    WebkitBackdropFilter: "blur(3px)",
                                }}
                            >
                                <textarea
                                    ref={refinedRef}
                                    className="form-control border-0 bg-transparent text-white-50"
                                    rows={4}
                                    value={refinedText}
                                    onChange={(e) => setRefinedText(e.target.value)}
                                    // User can now edit this before creating manga
                                    style={{
                                        minHeight: "120px",
                                        maxHeight: "180px",
                                        resize: "none",
                                        boxShadow: "none",
                                        outline: "none",
                                        overflowY: "auto",
                                    }}
                                />
                            </div>

                            {/* Create button */}
                            <button
                                className="btn btn-light rounded-2 fw-semibold py-3 d-block w-100 mb-2"
                                onClick={handleCreateClick}
                                disabled={isLoading}
                            >
                                ✦ Create My Manga
                            </button>
                        </div>
                    )}
                </main>

                {/* BOTTOM: helper text */}
                <footer className="mt-auto text-center text-white small mb-3">
                    AI will extract characters, scenes, and create panels automatically
                </footer>

                {/* Loading Overlay */}
                {isLoading && (
                    <div
                        className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                        style={{
                            backgroundColor: "rgba(0, 0, 0, 0.75)",
                            backdropFilter: "blur(4px)",
                            WebkitBackdropFilter: "blur(4px)",
                            zIndex: 1050,
                        }}
                    >
                        <div className="d-flex flex-column align-items-center text-center">
                            {/* icon */}
                            <div
                                className="d-flex align-items-center justify-content-center bg-white rounded-4 shadow-lg mb-4"
                                style={{width: 80, height: 80}}
                            >
                                <img
                                    src="/icons/ai_icon.jpg"
                                    alt="Loading Icon"
                                    className="img-fluid"
                                    style={{maxWidth: "70%", maxHeight: "70%"}}
                                />
                            </div>

                            {/* main text */}
                            <h4 className="text-white fw-bold mb-2">
                                Creating your manga...
                            </h4>

                            {/* sub text */}
                            <p className="text-white-50 mb-0">
                                AI is extracting characters, scenes and generating panels
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default HomePage;
