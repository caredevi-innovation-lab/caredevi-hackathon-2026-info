import { useNavigate } from 'react-router-dom'
import { Heart, Clock, Calendar, FileText, Activity, Zap, AlertCircle } from 'lucide-react'

import PatientSidebar from '../components/PatientSidebar'
import PatientTopNav from '../components/PatientTopNav'

const ACCESS_TOKEN_KEY = 'devcare_access_token'
const REFRESH_TOKEN_KEY = 'devcare_refresh_token'
const USERNAME_KEY = 'devcare_username'
const ROLE_KEY = 'devcare_role'

function PatientDashboardPage() {
  const navigate = useNavigate()
  const username = localStorage.getItem(USERNAME_KEY)

  function handleLogout() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USERNAME_KEY)
    localStorage.removeItem(ROLE_KEY)
    navigate('/')
  }

  return (
    <div className="flex min-h-screen bg-[var(--color-bg)]">
      <PatientSidebar username={username} onLogout={handleLogout} />

      <main className="flex-1 pt-16 md:pt-0 md:pl-0 flex flex-col">
        <PatientTopNav username={username} />
        
        <div className="flex-1 overflow-y-auto">
          <div className="site-container py-8">
            {/* Welcome Section */}
            <div className="mb-12 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8">
              <p className="text-sm font-bold uppercase tracking-[0.16em] text-[var(--color-primary)]">
                Welcome Back
              </p>
              <h1 className="mt-3 text-4xl font-bold sm:text-5xl text-[var(--color-text)]">
                Good morning, {username || 'Patient'}
              </h1>
              <p className="mt-4 text-base text-[var(--color-text-muted)]">
                You've reached 85% of your health goals this week. Keep up the consistent effort—your vital signs are showing significant data-driven progress.
              </p>
            </div>

            {/* Main Content Grid - Large Left Section + Right Sidebar */}
            <section className="mb-12 grid gap-8 lg:grid-cols-3">
              {/* Left Side - Large Featured Section */}
              <div className="lg:col-span-2">
                {/* Health Recovery Compliance Card */}
                <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm mb-8">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-bold uppercase tracking-[0.1em] text-[var(--color-text-muted)]">Recovery Compliance</h3>
                      <p className="mt-4 text-5xl font-bold text-[var(--color-primary)]">85%</p>
                      <p className="mt-2 text-sm text-[var(--color-text-muted)]">Weekly session completion rate</p>
                      
                      {/* Metrics Row */}
                      <div className="mt-6 grid grid-cols-2 gap-6">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-text-muted)]">Consistency</p>
                          <p className="mt-2 text-2xl font-bold text-[var(--color-accent)]">12 Days</p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-text-muted)]">Mobility Gain</p>
                          <p className="mt-2 text-2xl font-bold text-[var(--color-success)]">+4.2 pts</p>
                        </div>
                      </div>
                    </div>
                    <div className="ml-8 flex h-32 w-32 items-center justify-center rounded-full border-4 border-[var(--color-primary)] border-opacity-20 bg-[var(--color-primary)] bg-opacity-5">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-[var(--color-primary)]">85%</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Today's Exercise Queue */}
                <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-[var(--color-text)]">Today's Exercise Queue</h3>
                      <p className="mt-1 text-sm text-[var(--color-text-muted)]">3 exercises remaining • 25 mins total</p>
                    </div>
                    <button className="text-sm font-semibold text-[var(--color-primary)] hover:underline">
                      View all exercises →
                    </button>
                  </div>
                  <div className="mt-6 space-y-3">
                    {[
                      { name: 'Quad Strengthening', duration: '8 mins' },
                      { name: 'Knee Mobility Drills', duration: '10 mins' },
                      { name: 'Balance & Stability', duration: '7 mins' }
                    ].map((exercise, idx) => (
                      <div key={idx} className="flex items-center justify-between rounded-lg bg-[var(--color-bg)] p-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-primary)] bg-opacity-20">
                            <Activity className="h-3 w-3 text-[var(--color-primary)]" />
                          </div>
                          <span className="text-sm font-medium text-[var(--color-text)]">{exercise.name}</span>
                        </div>
                        <span className="text-xs text-[var(--color-text-muted)]">{exercise.duration}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Side - Two Stacked Cards with Divider */}
              <div className="flex flex-col gap-0">
                {/* Top Card - Next Session */}
                <div className="rounded-t-2xl border border-[var(--color-border)] border-b-0 bg-[#1e293b] p-8 text-white shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.1em] text-gray-400">Next Session</p>
                      <h3 className="mt-3 text-2xl font-bold">Post-ACL Mobility</h3>
                      <div className="mt-4 flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm">Starts in 15 mins</span>
                      </div>
                    </div>
                  </div>
                  <button className="btn-primary mt-6 w-full bg-white text-[var(--color-text)]">
                    Start Routine
                  </button>
                </div>

                {/* Divider Line */}
                <div className="border-b border-[var(--color-border)]"></div>

                {/* Bottom Card - Health Vitals */}
                <div className="rounded-b-2xl border border-[var(--color-border)] border-t-0 bg-[var(--color-surface)] p-8 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.1em] text-[var(--color-text-muted)]">Current Status</p>
                  <div className="mt-4 space-y-4">
                    <div>
                      <p className="text-xs text-[var(--color-text-muted)]">Blood Pressure</p>
                      <p className="mt-1 text-xl font-bold text-[var(--color-primary)]">120/80 mmHg</p>
                    </div>
                    <div>
                      <p className="text-xs text-[var(--color-text-muted)]">Heart Rate</p>
                      <p className="mt-1 text-xl font-bold text-[var(--color-primary)]">72 bpm</p>
                    </div>
                    <div className="pt-2">
                      <span className="inline-flex rounded-full bg-[var(--color-success)] bg-opacity-20 px-3 py-1 text-xs font-semibold text-[var(--color-success)]">
                        All Normal
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* AI Insights Section */}
            <section className="mb-12 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--color-primary)] text-white">
                  <Zap className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-[var(--color-text)]">Health Insights</h3>
                  <p className="mt-2 text-sm text-[var(--color-text-muted)]">
                    Based on your recent vitals and activity, your blood pressure remains stable at 120/80 mmHg. 
                    Continue with your current medication routine and maintain regular exercise. Your next checkup 
                    with Dr. Sarah Johnson is in 3 days.
                  </p>
                  <button className="mt-4 text-sm font-semibold text-[var(--color-primary)] hover:underline">
                    Learn more →
                  </button>
                </div>
              </div>
            </section>

            {/* Quick Actions Section */}
            <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-soft)] p-6">
              <h3 className="mb-4 text-lg font-bold text-[var(--color-text)]">Quick Actions</h3>
              <div className="flex flex-wrap gap-3">
                <button className="btn-primary flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Schedule Appointment
                </button>
                <button className="btn-secondary flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  View Medical Records
                </button>
                <button className="btn-secondary flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  View Lab Results
                </button>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

export default PatientDashboardPage
