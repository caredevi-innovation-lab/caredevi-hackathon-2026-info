import React from 'react';

const steps = [
  {
    number: '01',
    title: 'Connect Your Camera',
    description: 'Use any standard webcam or smartphone camera. No expensive hardware or sensors required.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    )
  },
  {
    number: '02',
    title: 'Perform Exercises',
    description: 'Follow guided therapy sessions while our AI tracks your form and provides real-time feedback.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    )
  },
  {
    number: '03',
    title: 'Track Recovery',
    description: 'Review detailed biomechanical reports and share progress with your clinician automatically.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    )
  }
];

function HowItWorksSection() {
  return (
    <section id="how-it-works" className="site-container py-20 sm:py-28">
      <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
        <div className="max-w-xl text-left">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.2em] text-[var(--color-primary)] mb-3">
            Process
          </p>
          <h2 className="text-3xl font-bold sm:text-4xl text-[var(--color-primary-strong)]">
            How DevCare Transforms Your Recovery
          </h2>
        </div>
        <p className="max-w-sm text-left text-[var(--color-text-muted)] text-sm">
          Simple, effective, and evidence-based. Our three-step process ensures you get clinical-grade care at home.
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {steps.map((step) => (
          <div key={step.number} className="relative group">
            <div className="mb-6 inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#E3F2FD] text-[#1E88E5] transition-transform group-hover:scale-110">
              {step.icon}
            </div>
            <div className="absolute top-0 right-0 text-6xl font-black text-[#F1F5F9] -z-10 select-none">
              {step.number}
            </div>
            <h3 className="text-xl font-bold mb-3 text-[#263238]">{step.title}</h3>
            <p className="text-[var(--color-text-muted)] text-sm leading-relaxed">
              {step.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default HowItWorksSection;