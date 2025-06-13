import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '@/store/slices/authSlice';
import type { RootState } from '@/store';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const accessToken = useSelector((state: RootState) => state.auth.accessToken);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
    { path: '/playlists', label: 'Playlists', icon: 'fas fa-list' },
    { path: '/liked', label: 'Liked Songs', icon: 'fas fa-heart' },
    { path: '/settings', label: 'Settings', icon: 'fas fa-cog' },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="glass-card m-4 p-4 sticky top-4 z-50">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-accent-gradient rounded-lg flex items-center justify-center">
              <i className="fas fa-music text-white text-sm"></i>
            </div>
            <h1 className="text-xl font-bold text-gradient-primary">
              Music Sync Hub
            </h1>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  location.pathname === item.path
                    ? 'bg-dark-card text-text-primary'
                    : 'text-text-secondary hover:text-text-primary hover:bg-dark-glass'
                }`}
              >
                <i className={item.icon}></i>
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              <i className="fas fa-sign-out-alt"></i>
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <nav className="md:hidden mt-4 flex justify-around border-t border-dark-border pt-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all duration-200 ${
                location.pathname === item.path
                  ? 'text-text-primary'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <i className={item.icon}></i>
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>
      </header>

      {/* Main Content */}
      <main className="px-4 pb-8">
        {children}
      </main>
    </div>
  );
} 