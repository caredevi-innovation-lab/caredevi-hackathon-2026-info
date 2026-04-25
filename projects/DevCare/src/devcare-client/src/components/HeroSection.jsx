import { Link } from 'react-router-dom'
import heroImage from '../assets/hero-therapy.png'

function HeroSection() {
  return (
    <section id="home" className="site-container pb-14 pt-12 sm:pb-20 sm:pt-16">
      <div className="grid items-center gap-10 lg:grid-cols-[1fr_1fr]">
        <div>
          <p className="inline-flex rounded-md bg-[#E3F2FD] px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-[#1E88E5]">
            Clinical Excellence
          </p>
          <h1 className="mt-4 text-4xl font-bold leading-tight sm:text-5xl lg:text-5xl text-[var(--color-primary-strong)]">
            AI-Powered Precision Therapy
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--color-text-muted)] sm:text-lg">
           AI-powered posture tracking for better, faster rehabilitation at home. DevCare brings clinical care into everyday recovery.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Link to="/register" className="btn-dark px-8 py-3">
              Get Started
            </Link>
            <a href="#demo" className="btn-secondary px-8 py-3 bg-white border-[#ECEFF1] text-[#263238] font-semibold">
              View Demo
            </a>
          </div>
        </div>

        <div className="relative">
          <img 
            src={heroImage} 
            alt="AI Posture Therapy" 
            className="rounded-3xl shadow-2xl w-full object-cover aspect-[4/3]"
          />
        </div>
      </div>
    </section>
  )
}

export default HeroSection