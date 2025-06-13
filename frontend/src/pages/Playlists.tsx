import React from 'react';

export default function PlaylistsPage() {
  // Mock data - will be replaced with real API calls
  const playlists = [
    {
      id: '1',
      name: 'My Favorites',
      platform: 'spotify',
      trackCount: 42,
      lastSync: '2 hours ago',
      status: 'synced',
    },
    {
      id: '2',
      name: 'Workout Mix',
      platform: 'youtube',
      trackCount: 28,
      lastSync: '1 day ago',
      status: 'pending',
    },
    {
      id: '3',
      name: 'Chill Vibes',
      platform: 'spotify',
      trackCount: 35,
      lastSync: 'Never',
      status: 'not-synced',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'synced': return 'text-success';
      case 'pending': return 'text-yellow-400';
      case 'not-synced': return 'text-text-secondary';
      default: return 'text-text-secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'synced': return 'fas fa-check-circle';
      case 'pending': return 'fas fa-clock';
      case 'not-synced': return 'fas fa-times-circle';
      default: return 'fas fa-question-circle';
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'spotify': return 'fab fa-spotify';
      case 'youtube': return 'fab fa-youtube';
      default: return 'fas fa-music';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'spotify': return 'text-spotify';
      case 'youtube': return 'text-youtube';
      default: return 'text-text-secondary';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center animate-fade-in-down">
        <h1 className="text-4xl font-bold text-gradient-primary mb-4">
          Your Playlists
        </h1>
        <p className="text-text-secondary text-lg max-w-2xl mx-auto">
          Manage and sync your playlists across all connected music platforms.
        </p>
      </div>

      {/* Actions Bar */}
      <div className="glass-card p-4 animate-fade-in-up">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="btn-primary">
              <i className="fas fa-sync-alt mr-2"></i>
              Sync All Playlists
            </button>
            <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg transition-colors">
              <i className="fas fa-plus mr-2"></i>
              Create Playlist
            </button>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search playlists..."
              className="input-glass w-64"
            />
            <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg transition-colors">
              <i className="fas fa-search"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Playlists Grid */}
      <div className="grid gap-6 animate-fade-in-up">
        {playlists.map((playlist, index) => (
          <div
            key={playlist.id}
            className="glass-card p-6 hover:bg-dark-card transition-all duration-300 group"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* Platform Icon */}
                <div className="w-12 h-12 bg-dark-card rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i className={`${getPlatformIcon(playlist.platform)} ${getPlatformColor(playlist.platform)} text-xl`}></i>
                </div>
                
                {/* Playlist Info */}
                <div>
                  <h3 className="text-xl font-semibold mb-1">{playlist.name}</h3>
                  <div className="flex items-center gap-4 text-sm text-text-secondary">
                    <span>
                      <i className="fas fa-music mr-1"></i>
                      {playlist.trackCount} tracks
                    </span>
                    <span>
                      <i className="fas fa-clock mr-1"></i>
                      Last sync: {playlist.lastSync}
                    </span>
                  </div>
                </div>
              </div>

              {/* Status and Actions */}
              <div className="flex items-center gap-4">
                {/* Status */}
                <div className="flex items-center gap-2">
                  <i className={`${getStatusIcon(playlist.status)} ${getStatusColor(playlist.status)}`}></i>
                  <span className={`text-sm font-medium ${getStatusColor(playlist.status)}`}>
                    {playlist.status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button className="px-3 py-2 bg-dark-card hover:bg-dark-border rounded-lg text-sm transition-colors">
                    <i className="fas fa-eye mr-1"></i>
                    View
                  </button>
                  <button className="px-3 py-2 bg-dark-card hover:bg-dark-border rounded-lg text-sm transition-colors">
                    <i className="fas fa-sync-alt mr-1"></i>
                    Sync
                  </button>
                  <button className="px-3 py-2 bg-dark-card hover:bg-dark-border rounded-lg text-sm transition-colors text-text-secondary hover:text-red-400">
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State (when no playlists) */}
      {playlists.length === 0 && (
        <div className="glass-card p-12 text-center animate-fade-in-up">
          <div className="w-16 h-16 bg-dark-card rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="fas fa-list text-text-secondary text-2xl"></i>
          </div>
          <h3 className="text-xl font-semibold mb-2">No Playlists Found</h3>
          <p className="text-text-secondary mb-6">
            Connect your music services to see your playlists here.
          </p>
          <button className="btn-primary">
            <i className="fas fa-plus mr-2"></i>
            Connect Services
          </button>
        </div>
      )}
    </div>
  );
} 