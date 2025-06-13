import React, { useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    autoSync: true,
    syncInterval: '1h',
    notifications: true,
    duplicateHandling: 'skip',
    theme: 'dark',
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center animate-fade-in-down">
        <h1 className="text-4xl font-bold text-gradient-primary mb-4">
          Settings
        </h1>
        <p className="text-text-secondary text-lg max-w-2xl mx-auto">
          Customize your Music Sync Hub experience and sync preferences.
        </p>
      </div>

      {/* Account Settings */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
          <i className="fas fa-user text-accent"></i>
          Account Settings
        </h2>
        
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value="user@example.com"
                className="input-glass w-full"
                disabled
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Display Name</label>
              <input
                type="text"
                value="Music Lover"
                className="input-glass w-full"
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <button className="btn-primary">
              <i className="fas fa-save mr-2"></i>
              Save Changes
            </button>
            <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg transition-colors">
              <i className="fas fa-key mr-2"></i>
              Change Password
            </button>
          </div>
        </div>
      </div>

      {/* Sync Settings */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
          <i className="fas fa-sync-alt text-accent"></i>
          Sync Settings
        </h2>
        
        <div className="space-y-6">
          {/* Auto Sync */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Auto Sync</h3>
              <p className="text-text-secondary text-sm">Automatically sync your music across platforms</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoSync}
                onChange={(e) => handleSettingChange('autoSync', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
            </label>
          </div>

          {/* Sync Interval */}
          <div>
            <label className="block text-sm font-medium mb-2">Sync Interval</label>
            <select
              value={settings.syncInterval}
              onChange={(e) => handleSettingChange('syncInterval', e.target.value)}
              className="input-glass w-full md:w-auto"
            >
              <option value="15m">Every 15 minutes</option>
              <option value="30m">Every 30 minutes</option>
              <option value="1h">Every hour</option>
              <option value="6h">Every 6 hours</option>
              <option value="24h">Daily</option>
            </select>
          </div>

          {/* Duplicate Handling */}
          <div>
            <label className="block text-sm font-medium mb-2">Duplicate Handling</label>
            <select
              value={settings.duplicateHandling}
              onChange={(e) => handleSettingChange('duplicateHandling', e.target.value)}
              className="input-glass w-full md:w-auto"
            >
              <option value="skip">Skip duplicates</option>
              <option value="replace">Replace existing</option>
              <option value="keep-both">Keep both versions</option>
            </select>
          </div>
        </div>
      </div>

      {/* Connected Services */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
          <i className="fas fa-link text-accent"></i>
          Connected Services
        </h2>
        
        <div className="space-y-4">
          {/* Spotify */}
          <div className="flex items-center justify-between p-4 bg-dark-glass rounded-lg">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-spotify bg-opacity-20 rounded-lg flex items-center justify-center">
                <i className="fab fa-spotify text-spotify text-xl"></i>
              </div>
              <div>
                <h3 className="font-medium">Spotify</h3>
                <p className="text-text-secondary text-sm">Not connected</p>
              </div>
            </div>
            <button className="btn-spotify">
              <i className="fas fa-link mr-2"></i>
              Connect
            </button>
          </div>

          {/* YouTube Music */}
          <div className="flex items-center justify-between p-4 bg-dark-glass rounded-lg">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-youtube bg-opacity-20 rounded-lg flex items-center justify-center">
                <i className="fab fa-youtube text-youtube text-xl"></i>
              </div>
              <div>
                <h3 className="font-medium">YouTube Music</h3>
                <p className="text-text-secondary text-sm">Not connected</p>
              </div>
            </div>
            <button className="btn-youtube">
              <i className="fas fa-link mr-2"></i>
              Connect
            </button>
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
          <i className="fas fa-bell text-accent"></i>
          Notifications
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Push Notifications</h3>
              <p className="text-text-secondary text-sm">Get notified about sync status and updates</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="glass-card p-6 animate-fade-in-up border border-red-500 border-opacity-20">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3 text-red-400">
          <i className="fas fa-exclamation-triangle"></i>
          Danger Zone
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-red-400">Clear All Data</h3>
              <p className="text-text-secondary text-sm">Remove all synced playlists and liked songs</p>
            </div>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
              <i className="fas fa-trash mr-2"></i>
              Clear Data
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-red-400">Delete Account</h3>
              <p className="text-text-secondary text-sm">Permanently delete your account and all data</p>
            </div>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
              <i className="fas fa-user-times mr-2"></i>
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 