import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import RequireAuth from '@/components/RequireAuth';
import Layout from '@/components/Layout';

const LoginPage = lazy(() => import('@pages/Login'));
const RegisterPage = lazy(() => import('@pages/Register'));
const DashboardPage = lazy(() => import('@pages/Dashboard'));
const PlaylistsPage = lazy(() => import('@pages/Playlists'));
const LikedPage = lazy(() => import('@pages/Liked'));
const SettingsPage = lazy(() => import('@pages/Settings'));

export default function App() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading…</div>}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<RequireAuth><Layout><DashboardPage /></Layout></RequireAuth>} />
        <Route path="/playlists" element={<RequireAuth><Layout><PlaylistsPage /></Layout></RequireAuth>} />
        <Route path="/liked" element={<RequireAuth><Layout><LikedPage /></Layout></RequireAuth>} />
        <Route path="/settings" element={<RequireAuth><Layout><SettingsPage /></Layout></RequireAuth>} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Suspense>
  );
} 