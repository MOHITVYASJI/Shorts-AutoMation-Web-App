import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Search, Plus, Video } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import VideoCard from '@/components/videos/VideoCard';
import VideoDetails from '@/components/videos/VideoDetails';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VideoLibrary = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [videos, setVideos] = useState([]);
  const [filteredVideos, setFilteredVideos] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPlatform, setFilterPlatform] = useState('all');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchVideos();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [videos, searchQuery, filterStatus, filterPlatform]);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/videos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVideos(response.data.videos || []);
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...videos];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(video =>
        video.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        video.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(video => video.status === filterStatus);
    }

    // Platform filter
    if (filterPlatform !== 'all') {
      filtered = filtered.filter(video =>
        video.published_platforms?.some(p => p.platform === filterPlatform)
      );
    }

    setFilteredVideos(filtered);
  };

  const handleVideoClick = (video) => {
    setSelectedVideo(video);
    setShowDetails(true);
  };

  const handleVideoDeleted = (videoId) => {
    setVideos(videos.filter(v => v.id !== videoId));
    setShowDetails(false);
    toast.success('Video deleted successfully');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="video-library-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Video Library</h1>
          <p className="text-slate-400">Manage all your created videos</p>
        </div>
        <Button
          onClick={() => navigate('/create')}
          className="bg-indigo-600 hover:bg-indigo-700"
          data-testid="create-new-video-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Video
        </Button>
      </div>

      {/* Filters */}
      <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search videos..."
                className="pl-10 bg-slate-800 border-slate-700 text-white"
                data-testid="search-videos-input"
              />
            </div>

            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="filter-status-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="rendering">Rendering</SelectItem>
                <SelectItem value="published">Published</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filterPlatform} onValueChange={setFilterPlatform}>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="filter-platform-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all">All Platforms</SelectItem>
                <SelectItem value="youtube">YouTube</SelectItem>
                <SelectItem value="instagram">Instagram</SelectItem>
                <SelectItem value="facebook">Facebook</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Videos Grid */}
      {filteredVideos.length === 0 ? (
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
          <CardContent className="py-16">
            <div className="text-center">
              <Video className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-white mb-2">No videos found</h3>
              <p className="text-slate-400 mb-6">
                {videos.length === 0
                  ? "You haven't created any videos yet"
                  : 'No videos match your filters'}
              </p>
              {videos.length === 0 && (
                <Button
                  onClick={() => navigate('/create')}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Video
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVideos.map(video => (
            <VideoCard
              key={video.id}
              video={video}
              onClick={() => handleVideoClick(video)}
            />
          ))}
        </div>
      )}

      {/* Video Details Modal */}
      {showDetails && selectedVideo && (
        <VideoDetails
          video={selectedVideo}
          open={showDetails}
          onClose={() => setShowDetails(false)}
          onVideoDeleted={handleVideoDeleted}
          onVideoUpdated={fetchVideos}
        />
      )}
    </div>
  );
};

export default VideoLibrary;