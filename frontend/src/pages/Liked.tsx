import React from 'react';

export default function LikedPage() {
  // Mock data - will be replaced with real API calls
  const likedSongs = [
    {
      id: '1',
      title: 'Blinding Lights',
      artist: 'The Weeknd',
      album: 'After Hours',
      platform: 'spotify',
      duration: '3:20',
      addedAt: '2 days ago',
    },
    {
      id: '2',
      title: 'Watermelon Sugar',
      artist: 'Harry Styles',
      album: 'Fine Line',
      platform: 'youtube',
      duration: '2:54',
      addedAt: '1 week ago',
    },
    {
      id: '3',
      title: 'Levitating',
      artist: 'Dua Lipa',
      album: 'Future Nostalgia',
      platform: 'spotify',
      duration: '3:23',
      addedAt: '3 days ago',
    },
  ];

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
          Liked Songs
        </h1>
        <p className="text-text-secondary text-lg max-w-2xl mx-auto">
          Your favorite tracks from all connected music platforms in one place.
        </p>
      </div>

      {/* Actions Bar */}
      <div className="glass-card p-4 animate-fade-in-up">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="btn-primary">
              <i className="fas fa-sync-alt mr-2"></i>
              Sync Liked Songs
            </button>
            <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg transition-colors">
              <i className="fas fa-download mr-2"></i>
              Export
            </button>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search songs..."
              className="input-glass w-64"
            />
            <button className="px-4 py-2 bg-dark-card hover:bg-dark-border rounded-lg transition-colors">
              <i className="fas fa-search"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Songs List */}
      <div className="glass-card animate-fade-in-up">
        <div className="p-6 border-b border-dark-border">
          <h3 className="text-xl font-semibold">Your Liked Songs ({likedSongs.length})</h3>
        </div>
        
        <div className="divide-y divide-dark-border">
          {likedSongs.map((song, index) => (
            <div
              key={song.id}
              className="p-6 hover:bg-dark-glass transition-all duration-300 group"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  {/* Album Art Placeholder */}
                  <div className="w-12 h-12 bg-dark-card rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <i className="fas fa-music text-text-secondary"></i>
                  </div>
                  
                  {/* Song Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="text-lg font-semibold truncate">{song.title}</h4>
                    <div className="flex items-center gap-4 text-sm text-text-secondary">
                      <span className="truncate">{song.artist}</span>
                      <span className="hidden sm:inline truncate">{song.album}</span>
                    </div>
                  </div>

                  {/* Platform */}
                  <div className="flex items-center gap-2">
                    <i className={`${getPlatformIcon(song.platform)} ${getPlatformColor(song.platform)}`}></i>
                    <span className="text-sm text-text-secondary hidden md:inline">
                      {song.platform.charAt(0).toUpperCase() + song.platform.slice(1)}
                    </span>
                  </div>

                  {/* Duration */}
                  <div className="text-sm text-text-secondary hidden sm:block">
                    {song.duration}
                  </div>

                  {/* Added Date */}
                  <div className="text-sm text-text-secondary hidden lg:block">
                    {song.addedAt}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  <button className="p-2 hover:bg-dark-card rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <i className="fas fa-play text-text-secondary hover:text-text-primary"></i>
                  </button>
                  <button className="p-2 hover:bg-dark-card rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <i className="fas fa-heart text-red-400"></i>
                  </button>
                  <button className="p-2 hover:bg-dark-card rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <i className="fas fa-ellipsis-v text-text-secondary hover:text-text-primary"></i>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {likedSongs.length === 0 && (
        <div className="glass-card p-12 text-center animate-fade-in-up">
          <div className="w-16 h-16 bg-dark-card rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="fas fa-heart text-text-secondary text-2xl"></i>
          </div>
          <h3 className="text-xl font-semibold mb-2">No Liked Songs</h3>
          <p className="text-text-secondary mb-6">
            Start liking songs on your connected platforms to see them here.
          </p>
          <button className="btn-primary">
            <i className="fas fa-sync-alt mr-2"></i>
            Sync Now
          </button>
        </div>
      )}

      {/* Stats Card */}
      <div className="glass-card p-6 animate-fade-in-up">
        <h3 className="text-xl font-semibold mb-4 text-center">Liked Songs Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gradient-accent">{likedSongs.length}</div>
            <div className="text-text-secondary text-sm">Total Songs</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">
              {likedSongs.filter(s => s.platform === 'spotify').length}
            </div>
            <div className="text-text-secondary text-sm">From Spotify</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">
              {likedSongs.filter(s => s.platform === 'youtube').length}
            </div>
            <div className="text-text-secondary text-sm">From YouTube</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gradient-accent">0</div>
            <div className="text-text-secondary text-sm">Duplicates</div>
          </div>
        </div>
      </div>
    </div>
  );
} 