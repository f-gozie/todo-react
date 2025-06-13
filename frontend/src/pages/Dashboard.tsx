import React, { useState } from 'react';

interface ServiceStatus {
  spotify: boolean;
  youtube: boolean;
}

export default function DashboardPage() {
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>({
    spotify: false,
    youtube: false,
  });

  const services = [
    {
      id: 'spotify',
      name: 'Spotify',
      icon: 'fab fa-spotify',
      color: 'spotify',
      description: 'Connect your Spotify account to sync playlists and liked songs',
      connectUrl: '/auth/spotify/login',
    },
    {
      id: 'youtube',
      name: 'YouTube Music',
      icon: 'fab fa-youtube',
      color: 'youtube',
      description: 'Connect your YouTube Music account to sync playlists and liked videos',
      connectUrl: '/auth/youtube/login',
    },
  ];

  const handleConnect = (serviceId: string) => {
    // This will be replaced with actual OAuth flow
    window.location.href = services.find(s => s.id === serviceId)?.connectUrl || '#';
  };

  const handleSync = async (type: 'liked' | 'playlists') => {
    try {
      // This will be replaced with actual API calls
      console.log(`Syncing ${type}...`);
      alert(`${type} sync started! (This is a placeholder)`);
    } catch (error) {
      console.error('Sync failed:', error);
      alert('Sync failed. Please try again.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center animate-fade-in-down">
        <h1 className="text-4xl font-bold text-gradient-primary mb-4">
          Welcome to Music Sync Hub
        </h1>
        <p className="text-text-secondary text-lg max-w-2xl mx-auto">
          Seamlessly synchronize your music across streaming platforms. Connect your accounts and let the magic happen.
        </p>
      </div>

      {/* Sync Actions */}
      <div className="grid md:grid-cols-2 gap-6 animate-fade-in-up">
        {/* Liked Songs Sync */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="absolute inset-0 bg-accent-gradient opacity-5 group-hover:opacity-10 transition-opacity"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-accent-gradient rounded-xl flex items-center justify-center">
                <i className="fas fa-heart text-white text-xl"></i>
              </div>
              <div>
                <h3 className="text-xl font-semibold">Liked Songs Sync</h3>
                <p className="text-text-secondary text-sm">Sync your favorite tracks across platforms</p>
              </div>
            </div>
            <p className="text-text-secondary mb-6">
              Analyze and synchronize your liked songs across all connected platforms with one click.
            </p>
            <button
              onClick={() => handleSync('liked')}
              className="btn-primary w-full"
              disabled={!serviceStatus.spotify && !serviceStatus.youtube}
            >
              <i className="fas fa-sync-alt mr-2"></i>
              Analyze Liked Songs
            </button>
          </div>
        </div>

        {/* Playlists Sync */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="absolute inset-0 bg-secondary-gradient opacity-5 group-hover:opacity-10 transition-opacity"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-secondary-gradient rounded-xl flex items-center justify-center">
                <i className="fas fa-list text-white text-xl"></i>
              </div>
              <div>
                <h3 className="text-xl font-semibold">Playlist Sync</h3>
                <p className="text-text-secondary text-sm">Sync playlists and their tracks</p>
              </div>
            </div>
            <p className="text-text-secondary mb-6">
              Analyze your playlists across all platforms and synchronize missing playlists and tracks.
            </p>
            <button
              onClick={() => handleSync('playlists')}
              className="btn-primary w-full"
              disabled={!serviceStatus.spotify && !serviceStatus.youtube}
            >
              <i className="fas fa-search mr-2"></i>
              Analyze Playlists
            </button>
          </div>
        </div>
      </div>

      {/* Service Connection Cards */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-center mb-6">Connect Your Music Services</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {services.map((service, index) => (
            <div
              key={service.id}
              className="glass-card p-6 relative overflow-hidden group animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Service color accent */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-${service.color}`}></div>
              
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${service.color} bg-opacity-20`}>
                    <i className={`${service.icon} text-${service.color} text-2xl`}></i>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">{service.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <div className={serviceStatus[service.id as keyof ServiceStatus] ? 'status-connected' : 'status-disconnected'}></div>
                      <span className="text-sm text-text-secondary">
                        {serviceStatus[service.id as keyof ServiceStatus] ? 'Connected' : 'Not connected'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <p className="text-text-secondary mb-6">{service.description}</p>

              <div className="space-y-3">
                {!serviceStatus[service.id as keyof ServiceStatus] ? (
                  <button
                    onClick={() => handleConnect(service.id)}
                    className={`btn-${service.color} w-full py-3 px-6 rounded-xl font-medium transition-all duration-300`}
                  >
                    <i className="fas fa-link mr-2"></i>
                    Connect {service.name}
                  </button>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg text-sm transition-colors">
                      <i className="fas fa-user mr-2"></i>
                      Profile
                    </button>
                    <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg text-sm transition-colors">
                      <i className="fas fa-list mr-2"></i>
                      Playlists
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h3 className="text-xl font-semibold mb-4 text-center">Quick Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gradient-accent">0</div>
            <div className="text-text-secondary text-sm">Connected Services</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">0</div>
            <div className="text-text-secondary text-sm">Synced Playlists</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">0</div>
            <div className="text-text-secondary text-sm">Liked Songs</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">0</div>
            <div className="text-text-secondary text-sm">Last Sync</div>
          </div>
        </div>
      </div>
    </div>
  );
} 