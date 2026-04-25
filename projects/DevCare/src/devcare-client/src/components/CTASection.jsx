import { Link } from 'react-router-dom';

function CTASection() {
  return (
    <section className="site-container py-20 sm:py-28 text-center">
      <h2 className="text-4xl font-bold sm:text-5xl text-[var(--color-primary-strong)] mb-6">
        Ready to Transform Your Practice?
      </h2>
      
      <p className="max-w-2xl mx-auto text-[var(--color-text-muted)] text-base sm:text-lg mb-10">
        Join hundreds of medical professionals using DevCare to deliver superior rehabilitation experiences remotely.
      </p>
      
      <div className="flex flex-wrap justify-center gap-4">
        <Link to="/register" className="btn-dark px-10 py-3">
          Get Started Free
        </Link>
      </div>
    </section>
  );
}

export default CTASection;
