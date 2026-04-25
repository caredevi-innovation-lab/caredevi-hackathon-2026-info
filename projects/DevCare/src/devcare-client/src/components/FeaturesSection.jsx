const features = [
  {
    tag: 'AI Posture Detection',
    title: 'AI Posture Detection',
    description:
      'Advanced skeletal mapping tracks joints in real-time, providing immediate corrective feedback during rehabilitation exercises without the need for wearable sensors.',
    icon: (
      <svg className="w-8 h-8 text-[#1E88E5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    )
  },
  {
    tag: 'Outcome Analytics',
    title: 'Outcome Analytics',
    description:
      'Longitudinal tracking of patient recovery progress through automated biomechanical reporting.',
    icon: (
      <svg className="w-8 h-8 text-[#1E88E5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    showProgress: true
  },
  {
    tag: 'Smart Telerehab',
    title: 'Smart Telerehab',
    description:
      'Seamlessly connect with therapists through high-definition encrypted video integrated with clinical data overlays.',
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    ),
    dark: true
  },
]

function FeaturesSection() {
  return (
    <section id="features" className="site-container py-14 sm:py-24 text-center">
      <div className="mb-16">
        <h2 className="text-3xl font-bold sm:text-4xl text-[var(--color-primary-strong)]">
          The New Standard of Care
        </h2>
        <p className="mt-4 mx-auto max-w-2xl text-[var(--color-text-muted)] text-sm sm:text-base">
          Our platform combines computer vision with clinical expertise to provide a recovery experience that is both data-driven and human-centric.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3 text-left">
        {features.map((feature) => (
          <article
            key={feature.title}
            className={`elevated-card rounded-2xl border border-[var(--color-border)] p-8 ${
              feature.dark ? 'bg-[#1a233a] text-white shadow-xl' : 'bg-white'
            }`}
          >
            <div className="mb-6">{feature.icon}</div>
            <h3 className={`text-xl font-bold ${feature.dark ? 'text-white' : 'text-[#263238]'}`}>
              {feature.title}
            </h3>
            <p className={`mt-3 text-sm leading-6 ${feature.dark ? 'text-gray-300' : 'text-[#607D8B]'}`}>
              {feature.description}
            </p>
            {feature.showProgress && (
              <div className="mt-8 space-y-3">
                <div className="h-1.5 w-full bg-[#ECEFF1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#1E88E5] w-[85%]"></div>
                </div>
                <div className="h-1.5 w-full bg-[#ECEFF1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#1a233a] w-[55%]"></div>
                </div>
              </div>
            )}
            {feature.dark && (
              <a href="#" className="mt-8 inline-flex items-center text-sm font-bold text-white hover:underline">
                Learn more <span className="ml-1">→</span>
              </a>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}

export default FeaturesSection