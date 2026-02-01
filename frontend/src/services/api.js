/**
 * API Service Layer for AutoShorts AI
 * 
 * Handles all HTTP requests to the backend API
 */

import axios from 'axios';

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Authentication APIs
 */
export const authAPI = {
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  googleAuth: async (googleToken) => {
    const response = await api.post('/auth/google', { token: googleToken });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/profile', profileData);
    return response.data;
  },
};

/**
 * Platform Integration APIs
 */
export const platformsAPI = {
  // Get all connected accounts
  getAccounts: async () => {
    const response = await api.get('/platforms/accounts');
    return response.data;
  },

  // YouTube
  getYouTubeAuthUrl: async () => {
    const response = await api.get('/platforms/youtube/auth-url');
    return response.data;
  },

  youtubeCallback: async (code) => {
    const response = await api.post('/platforms/youtube/callback', { code });
    return response.data;
  },

  disconnectYouTube: async (accountId) => {
    const response = await api.delete(`/platforms/youtube/accounts/${accountId}`);
    return response.data;
  },

  // Instagram
  getInstagramAuthUrl: async () => {
    const response = await api.get('/platforms/instagram/auth-url');
    return response.data;
  },

  instagramCallback: async (code) => {
    const response = await api.post('/platforms/instagram/callback', { code });
    return response.data;
  },

  disconnectInstagram: async (accountId) => {
    const response = await api.delete(`/platforms/instagram/accounts/${accountId}`);
    return response.data;
  },

  // Facebook
  getFacebookAuthUrl: async () => {
    const response = await api.get('/platforms/facebook/auth-url');
    return response.data;
  },

  facebookCallback: async (code) => {
    const response = await api.post('/platforms/facebook/callback', { code });
    return response.data;
  },

  disconnectFacebook: async (accountId) => {
    const response = await api.delete(`/platforms/facebook/accounts/${accountId}`);
    return response.data;
  },

  // Disconnect any account
  disconnectAccount: async (accountId) => {
    const response = await api.delete(`/platforms/accounts/${accountId}`);
    return response.data;
  },
};

/**
 * Content Generation APIs
 */
export const contentAPI = {
  // Get available options
  getNiches: async () => {
    const response = await api.get('/content/niches');
    return response.data;
  },

  getLanguages: async () => {
    const response = await api.get('/content/languages');
    return response.data;
  },

  getDurations: async () => {
    const response = await api.get('/content/durations');
    return response.data;
  },

  getVoices: async () => {
    const response = await api.get('/content/voices');
    return response.data;
  },

  // Generate script
  generateScript: async (params) => {
    const response = await api.post('/content/generate-script', params);
    return response.data;
  },

  // Generate voice
  generateVoice: async (params) => {
    const response = await api.post('/content/generate-voice', params);
    return response.data;
  },

  generateVoiceFromScript: async (params) => {
    const response = await api.post('/content/generate-voice-from-script', params);
    return response.data;
  },

  // Generate visuals
  generateVisuals: async (params) => {
    const response = await api.post('/content/generate-visuals', params);
    return response.data;
  },

  // Generate complete content package
  generateComplete: async (params) => {
    const response = await api.post('/content/generate-complete', params);
    return response.data;
  },
};

/**
 * Video APIs
 */
export const videosAPI = {
  // Render video
  renderVideo: async (renderData) => {
    const response = await api.post('/videos/render', renderData);
    return response.data;
  },

  // Check render status
  getRenderStatus: async (jobId) => {
    const response = await api.get(`/videos/render/${jobId}/status`);
    return response.data;
  },

  // Get all videos
  getVideos: async (params = {}) => {
    const response = await api.get('/videos', { params });
    return response.data;
  },

  // Get single video
  getVideo: async (videoId) => {
    const response = await api.get(`/videos/${videoId}`);
    return response.data;
  },

  // Update video
  updateVideo: async (videoId, videoData) => {
    const response = await api.put(`/videos/${videoId}`, videoData);
    return response.data;
  },

  // Delete video
  deleteVideo: async (videoId) => {
    const response = await api.delete(`/videos/${videoId}`);
    return response.data;
  },

  // Download video
  downloadVideo: async (jobId) => {
    const response = await api.get(`/videos/render/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

/**
 * Publishing APIs
 */
export const publishAPI = {
  // Publish to YouTube
  publishToYouTube: async (publishData) => {
    const response = await api.post('/publish/youtube', publishData);
    return response.data;
  },

  // Publish to Instagram
  publishToInstagram: async (publishData) => {
    const response = await api.post('/publish/instagram', publishData);
    return response.data;
  },

  // Publish to Facebook
  publishToFacebook: async (publishData) => {
    const response = await api.post('/publish/facebook', publishData);
    return response.data;
  },

  // Publish to multiple platforms
  publishToMultiple: async (publishData) => {
    const response = await api.post('/publish/multi', publishData);
    return response.data;
  },

  // Schedule publishing
  schedulePublish: async (scheduleData) => {
    const response = await api.post('/publish/schedule', scheduleData);
    return response.data;
  },

  // Get scheduled publishes
  getScheduledPublishes: async () => {
    const response = await api.get('/publish/schedule');
    return response.data;
  },

  // Cancel scheduled publish
  cancelScheduledPublish: async (scheduleId) => {
    const response = await api.delete(`/publish/schedule/${scheduleId}`);
    return response.data;
  },
};

/**
 * Analytics APIs
 */
export const analyticsAPI = {
  // Trigger analytics sync
  syncAnalytics: async () => {
    const response = await api.post('/analytics/sync');
    return response.data;
  },

  // Get video analytics
  getVideoAnalytics: async (videoId) => {
    const response = await api.get(`/analytics/video/${videoId}`);
    return response.data;
  },

  // Get account analytics
  getAccountAnalytics: async (accountId) => {
    const response = await api.get(`/analytics/account/${accountId}`);
    return response.data;
  },

  // Get platform analytics
  getPlatformAnalytics: async (platform) => {
    const response = await api.get(`/analytics/platform/${platform}`);
    return response.data;
  },
};

/**
 * Dashboard APIs
 */
export const dashboardAPI = {
  // Get dashboard summary
  getSummary: async () => {
    const response = await api.get('/dashboard/summary');
    return response.data;
  },

  // Get platform stats
  getPlatformStats: async () => {
    const response = await api.get('/dashboard/platform-stats');
    return response.data;
  },

  // Get top videos
  getTopVideos: async (limit = 10) => {
    const response = await api.get('/dashboard/top-videos', { params: { limit } });
    return response.data;
  },

  // Get upload calendar
  getUploadCalendar: async () => {
    const response = await api.get('/dashboard/upload-calendar');
    return response.data;
  },
};

/**
 * Insights APIs
 */
export const insightsAPI = {
  // Get AI recommendations
  getRecommendations: async () => {
    const response = await api.get('/insights/recommendations');
    return response.data;
  },

  // Get best upload time
  getBestUploadTime: async () => {
    const response = await api.get('/insights/best-time');
    return response.data;
  },

  // Get best performing niche
  getBestNiche: async () => {
    const response = await api.get('/insights/best-niche');
    return response.data;
  },
};

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
