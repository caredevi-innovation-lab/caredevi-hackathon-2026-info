import { useState } from "react";
import { useNavigate } from "react-router-dom";

import CTASection from "../components/CTASection";
import AuthSection from "../components/AuthSection";
import FeaturesSection from "../components/FeaturesSection";
import HowItWorksSection from "../components/HowItWorksSection";
import HeroSection from "../components/HeroSection";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function LandingPage() {
    return (
        <div className="app-shell">
            <Navbar/>

            <>
                <section id="home">
                    <HeroSection />
                </section>
                <section id="features" className="bg-[#F8FAFC]">
                    <FeaturesSection />
                </section>
                <section id="how-it-works">
                    <HowItWorksSection />
                </section>
                <section id="cta">
                    <CTASection />
                </section>
            </>
            
            <Footer />
        </div>
    );
}

export default LandingPage;
