import { useState } from 'react'
import { Search, Bell, User, ChevronDown } from 'lucide-react'

function PatientTopNav({ username }) {
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [notifications, setNotifications] = useState([
    { id: 1, message: 'Appointment reminder: Dr. Johnson tomorrow at 10:00 AM', time: '2 hours ago' },
    { id: 2, message: 'Your prescription Lisinopril will expire in 5 days', time: '1 day ago' },
    { id: 3, message: 'Lab results are ready for review', time: '3 days ago' },
  ])
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)

  return (
    <div className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Search Bar */}
        <div className="hidden flex-1 max-w-md lg:flex">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-[var(--color-text-muted)]" />
            <input
              type="text"
              placeholder="Search appointments, prescriptions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-soft)] py-2 pl-10 pr-4 text-sm text-[var(--color-text)] placeholder-[var(--color-text-muted)] transition-all duration-200 focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-opacity-10"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4 ml-auto">
          {/* Mobile Search Icon */}
          <button className="lg:hidden text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors">
            <Search className="h-5 w-5" />
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className="relative text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors"
            >
              <Bell className="h-5 w-5" />
              {notifications.length > 0 && (
                <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--color-danger)] text-xs font-bold text-white">
                  {notifications.length}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {isNotificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] shadow-lg">
                <div className="border-b border-[var(--color-border)] p-4">
                  <h3 className="text-sm font-semibold text-[var(--color-text)]">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length > 0 ? (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className="border-b border-[var(--color-border)] p-4 hover:bg-[var(--color-surface-soft)] transition-colors cursor-pointer"
                      >
                        <p className="text-sm text-[var(--color-text)]">{notification.message}</p>
                        <p className="mt-1 text-xs text-[var(--color-text-muted)]">{notification.time}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-sm text-[var(--color-text-muted)]">
                      No notifications
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Profile Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className="flex items-center gap-2 rounded-lg hover:bg-[var(--color-surface-soft)] px-3 py-2 transition-colors"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-semibold text-white">
                {(username || 'P').charAt(0).toUpperCase()}
              </div>
              <span className="hidden text-sm font-medium text-[var(--color-text)] sm:inline">
                {username || 'Patient'}
              </span>
              <ChevronDown className="h-4 w-4 text-[var(--color-text-muted)]" />
            </button>

            {/* Profile Dropdown Menu */}
            {isProfileOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] shadow-lg">
                <div className="p-4 border-b border-[var(--color-border)]">
                  <p className="text-sm font-semibold text-[var(--color-text)]">{username || 'Patient'}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">patient@example.com</p>
                </div>
                <div className="p-2">
                  <button className="flex w-full items-center gap-2 rounded px-3 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-surface-soft)] transition-colors">
                    <User className="h-4 w-4" />
                    <span>View Profile</span>
                  </button>
                  <button className="flex w-full items-center gap-2 rounded px-3 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-surface-soft)] transition-colors">
                    <span>Settings</span>
                  </button>
                </div>
                <div className="border-t border-[var(--color-border)] p-2">
                  <button className="flex w-full items-center gap-2 rounded px-3 py-2 text-sm text-[var(--color-danger)] hover:bg-[var(--color-danger)] hover:bg-opacity-10 transition-colors">
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PatientTopNav
