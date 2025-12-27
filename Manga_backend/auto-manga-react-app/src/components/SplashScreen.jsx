// src/components/SplashScreen.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

function SplashScreen() {
    const navigate = useNavigate();

    // Background style
    const bgStyle = {
        backgroundImage: "url('/luffy_bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#000",
        minHeight: "100vh",
    };

    // Overlay style
    const overlayStyle = {
        background:
            "linear-gradient(135deg, rgba(0, 0, 0, 0.55), rgba(10, 10, 10, 0.35))",
        backdropFilter: "blur(2px)",
        WebkitBackdropFilter: "blur(2px)",
    };

    return (
        <div className="position-relative w-100" style={bgStyle}>
            {/* Dark Glass Overlay */}
            <div
                className="position-absolute top-0 start-0 w-100 h-100"
                style={overlayStyle}
            />

            {/* Main Content Layer */}
            <div className="position-relative d-flex flex-column" style={{ minHeight: "100vh" }}>

                {/* TOP SECTION */}
                <div className="flex-grow-1 d-flex flex-column align-items-center justify-content-center">
                    {/* Icon Container */}
                    <div
                        className="d-flex align-items-center justify-content-center bg-white rounded-4 shadow-lg"
                        style={{ width: 96, height: 96 }}
                    >
                        <img
                            src="/icons/ai_icon.jpg"
                            alt="Main Icon"
                            className="img-fluid"
                            style={{ maxWidth: "70%", maxHeight: "70%" }}
                        />
                    </div>

                    <div style={{ height: "24px" }} />

                    {/* Title */}
                    <h1 className="fw-bold text-white text-center display-6">Auto Manga</h1>

                    {/* Subtitle */}
                    <p
                        className="text-white text-center mt-2"
                        style={{ maxWidth: "320px" }}
                    >
                        Transform your stories into manga with AI
                    </p>

                    <div style={{ height: "24px" }} />

                    {/* Navigation Button - No API calls here, just routing */}
                    <button
                        className="btn btn-light btn-lg px-5 py-3 fw-semibold rounded-2 shadow"
                        onClick={() => navigate("/home")}
                    >
                        Get Started
                    </button>
                </div>

                {/* BOTTOM FEATURES SECTION */}
                <div className="container mb-5">
                    <div className="row text-center justify-content-center g-4">
                        {/* Feature 1 */}
                        <div className="col-4 d-flex flex-column align-items-center">
                            <img
                                src="/icons/ai_1.jpg"
                                alt="Smart AI"
                                className="mb-2 rounded-2"
                                style={{ width: 48, height: 48, objectFit: "cover" }}
                            />
                            <div className="fw-semibold text-white small">Smart AI</div>
                            <div className="text-white small">
                                Auto-extracts details
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="col-4 d-flex flex-column align-items-center">
                            <img
                                src="/icons/controll.jpg"
                                alt="Full Control"
                                className="mb-2 rounded-2"
                                style={{ width: 48, height: 48, objectFit: "cover" }}
                            />
                            <div className="fw-semibold text-white small">Full Control</div>
                            <div className="text-white small">
                                Edit panels anytime
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="col-4 d-flex flex-column align-items-center">
                            <img
                                src="/icons/version.jpg"
                                alt="Variations"
                                className="mb-2 rounded-2"
                                style={{ width: 48, height: 48, objectFit: "cover" }}
                            />
                            <div className="fw-semibold text-white small">Variations</div>
                            <div className="text-white small">
                                Pick your version
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default SplashScreen;