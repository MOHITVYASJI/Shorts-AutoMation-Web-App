# 🏗️ AutoShorts AI - Architecture Blueprint

## 📊 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │Dashboard │ Create   │ Videos   │Analytics │ Accounts     │  │
│  │  Home    │ Video    │ Library  │ Insights │ Management   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/REST API
┌───────────────────────────┴─────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     API GATEWAY                          │   │
│  │  (Auth Middleware, Rate Limiting, CORS)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────┬────────────┬────────────┬─────────────────┐   │
│  │   AUTH     │  CONTENT   │   VIDEO    │   PUBLISHING    │   │
│  │  SERVICE   │  SERVICE   │  SERVICE   │    SERVICE      │   │
│  └────────────┴────────────┴────────────┴─────────────────┘   │
│                                                                  │
│  ┌────────────┬────────────┬────────────┬─────────────────┐   │
│  │ ANALYTICS  │ INSIGHTS   │ SCHEDULER  │  QUEUE          │   │
│  │  SERVICE   │  ENGINE    │  SERVICE   │  PROCESSOR      │   │
│  └────────────┴────────────┴────────────┴─────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                      DATA LAYER (MongoDB)                        │
│  ┌────────┬────────┬────────┬────────┬────────┬────────────┐  │
│  │ Users  │Accounts│Videos  │Analytics│Queue  │Schedules   │  │
│  └────────┴────────┴────────┴────────┴────────┴────────────┘  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │ OpenAI   │ Gemini   │ElevenLabs│  YouTube │  Instagram   │  │
│  │   API    │   API    │   API    │   API    │     API      │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
│  ┌──────────┬──────────┬──────────────────────────────────┐   │
│  │ Facebook │  Pexels  │         FFmpeg (Local)            │   │
│  │   API    │   API    │                                   │   │
│  └──────────┴──────────┴──────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ DATABASE SCHEMA (MongoDB Collections)

### 1. **users**
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password_hash: String,
  full_name: String,
  google_id: String (optional, for OAuth),
  created_at: DateTime,
  subscription_plan: String (free/pro - for future),
  is_active: Boolean
}
```

### 2. **connected_accounts**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users, indexed),
  platform: String (youtube/instagram/facebook),
  account_id: String (platform's user/page ID),
  account_name: String,
  account_email: String,
  access_token: String (encrypted),
  refresh_token: String (encrypted),
  token_expiry: DateTime,
  connected_at: DateTime,
  status: String (active/disconnected)
}
```

### 3. **videos**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users, indexed),
  title: String,
  description: String,
  hashtags: [String],
  
  // Content details
  script: {
    hook: String,
    story: String,
    ending: String
  },
  niche: String,
  language: String,
  duration: Number (seconds),
  
  // File paths
  video_file_path: String,
  thumbnail_path: String,
  voice_file_path: String,
  
  // Generation details
  visuals: [String], // URLs or paths
  background_music: String,
  captions_enabled: Boolean,
  
  // Status
  status: String (draft/rendering/published),
  render_job_id: String (optional),
  
  // Publishing info
  published_platforms: [{
    platform: String,
    account_id: ObjectId,
    platform_video_id: String,
    published_at: DateTime,
    url: String
  }],
  
  created_at: DateTime,
  updated_at: DateTime
}
```

### 4. **analytics**
```javascript
{
  _id: ObjectId,
  video_id: ObjectId (ref: videos, indexed),
  platform: String (indexed),
  account_id: ObjectId (ref: connected_accounts),
  platform_video_id: String,
  
  // Metrics
  views: Number,
  likes: Number,
  comments: Number,
  shares: Number,
  retention_percentage: Number (optional),
  
  // Time-series data
  metrics_history: [{
    date: DateTime,
    views: Number,
    likes: Number,
    comments: Number,
    shares: Number
  }],
  
  last_synced_at: DateTime,
  created_at: DateTime
}
```

### 5. **render_queue**
```javascript
{
  _id: ObjectId,
  job_id: String (unique, indexed),
  user_id: ObjectId (ref: users),
  video_id: ObjectId (ref: videos),
  
  // Render inputs
  script: Object,
  voice_url: String,
  visuals: [String],
  background_music: String,
  captions_enabled: Boolean,
  
  // Status tracking
  status: String (pending/processing/completed/failed),
  progress: Number (0-100),
  error_message: String (optional),
  
  output_file_path: String (when completed),
  
  created_at: DateTime,
  started_at: DateTime,
  completed_at: DateTime
}
```

### 6. **schedules**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users, indexed),
  video_id: ObjectId (ref: videos),
  
  platform: String,
  account_id: ObjectId (ref: connected_accounts),
  
  scheduled_time: DateTime (indexed),
  status: String (pending/published/failed/cancelled),
  
  // Metadata for publishing
  metadata: {
    title: String,
    description: String,
    hashtags: [String],
    visibility: String
  },
  
  error_message: String (optional),
  published_at: DateTime (optional),
  
  created_at: DateTime
}
```

---

## 🔌 API ENDPOINTS STRUCTURE

### **Authentication Routes** (`/api/auth`)
```
POST   /api/auth/signup           - Create new user
POST   /api/auth/login            - Email/password login
POST   /api/auth/google           - Google OAuth login
GET    /api/auth/profile          - Get current user profile
PUT    /api/auth/profile          - Update user profile
POST   /api/auth/refresh-token    - Refresh JWT token
```

### **Platform Integration Routes** (`/api/platforms`)
```
GET    /api/platforms/youtube/auth-url          - Get YouTube OAuth URL
POST   /api/platforms/youtube/callback          - Handle OAuth callback
GET    /api/platforms/instagram/auth-url        - Get Instagram OAuth URL
POST   /api/platforms/instagram/callback        - Handle OAuth callback
GET    /api/platforms/facebook/auth-url         - Get Facebook OAuth URL
POST   /api/platforms/facebook/callback         - Handle OAuth callback

GET    /api/platforms/accounts                  - List all connected accounts
DELETE /api/platforms/accounts/{account_id}    - Disconnect account
```

### **Content Generation Routes** (`/api/content`)
```
POST   /api/content/generate-script       - Generate AI script
POST   /api/content/generate-voice        - Generate TTS audio
POST   /api/content/generate-visuals      - Get AI images/stock footage
GET    /api/content/niches                - Get available niches
GET    /api/content/languages             - Get supported languages
```

### **Video Routes** (`/api/videos`)
```
POST   /api/videos/render                 - Start video rendering job
GET    /api/videos/render/{job_id}/status - Check render status
GET    /api/videos/render/{job_id}/download - Download rendered video

GET    /api/videos                        - List user's videos
GET    /api/videos/{video_id}             - Get single video details
PUT    /api/videos/{video_id}             - Update video metadata
DELETE /api/videos/{video_id}             - Delete video
```

### **Publishing Routes** (`/api/publish`)
```
POST   /api/publish/youtube               - Publish to YouTube
POST   /api/publish/instagram             - Publish to Instagram
POST   /api/publish/facebook              - Publish to Facebook
POST   /api/publish/multi                 - Publish to multiple platforms

POST   /api/publish/schedule              - Schedule a publish
GET    /api/publish/schedule              - List scheduled publishes
DELETE /api/publish/schedule/{id}         - Cancel scheduled publish
```

### **Analytics Routes** (`/api/analytics`)
```
POST   /api/analytics/sync                     - Trigger manual sync
GET    /api/analytics/video/{video_id}         - Get video analytics
GET    /api/analytics/account/{account_id}     - Get account analytics
GET    /api/analytics/platform/{platform}      - Get platform-wise analytics
```

### **Dashboard Routes** (`/api/dashboard`)
```
GET    /api/dashboard/summary             - Get dashboard summary
GET    /api/dashboard/platform-stats      - Get platform comparison stats
GET    /api/dashboard/top-videos          - Get best performing videos
GET    /api/dashboard/upload-calendar     - Get upload calendar data
```

### **Insights Routes** (`/api/insights`)
```
GET    /api/insights/recommendations      - Get AI-powered suggestions
GET    /api/insights/best-time            - Get best upload time
GET    /api/insights/best-niche           - Get best performing niche
```

---

## 📁 BACKEND FILE STRUCTURE

```
/app/backend/
├── server.py                      # Main FastAPI app
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
│
├── config/
│   ├── __init__.py
│   ├── database.py                # MongoDB connection
│   ├── settings.py                # App settings (from .env)
│   └── constants.py               # App constants (niches, languages)
│
├── models/
│   ├── __init__.py
│   ├── user.py                    # User Pydantic models
│   ├── account.py                 # Connected account models
│   ├── video.py                   # Video models
│   ├── analytics.py               # Analytics models
│   └── schedule.py                # Schedule models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                    # Auth endpoints
│   ├── platforms.py               # Platform integration endpoints
│   ├── content.py                 # Content generation endpoints
│   ├── videos.py                  # Video CRUD endpoints
│   ├── publish.py                 # Publishing endpoints
│   ├── analytics.py               # Analytics endpoints
│   ├── dashboard.py               # Dashboard endpoints
│   └── insights.py                # Insights endpoints
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py            # Authentication logic
│   ├── content_generator.py      # AI script generation
│   ├── tts_generator.py           # Text-to-speech
│   ├── visual_generator.py        # AI images + stock footage
│   ├── video_renderer.py          # FFmpeg video rendering
│   ├── youtube_publisher.py       # YouTube API integration
│   ├── instagram_publisher.py     # Instagram API integration
│   ├── facebook_publisher.py      # Facebook API integration
│   ├── analytics_sync.py          # Analytics data fetching
│   ├── insights_engine.py         # AI insights generation
│   └── scheduler_service.py       # Background job scheduler
│
├── middleware/
│   ├── __init__.py
│   ├── auth_middleware.py         # JWT validation
│   └── error_handler.py           # Global error handling
│
├── utils/
│   ├── __init__.py
│   ├── jwt_utils.py               # JWT token helpers
│   ├── encryption.py              # Token encryption
│   ├── validators.py              # Input validation
│   └── file_utils.py              # File storage helpers
│
├── workers/
│   ├── __init__.py
│   ├── render_worker.py           # Background video rendering
│   └── scheduler_worker.py        # Scheduled publishing worker
│
└── storage/                       # Local file storage
    ├── videos/                    # Rendered videos
    ├── audio/                     # Generated audio files
    ├── images/                    # Downloaded/generated images
    └── temp/                      # Temporary files
```

---

## 🎨 FRONTEND FILE STRUCTURE

```
/app/frontend/src/
├── index.js                       # Entry point
├── App.js                         # Main app component
├── App.css                        # Main styles
├── index.css                      # Global styles
│
├── components/
│   ├── ui/                        # Shadcn UI components (pre-existing)
│   │   ├── button.jsx
│   │   ├── card.jsx
│   │   ├── input.jsx
│   │   ├── select.jsx
│   │   └── ...
│   │
│   ├── layout/
│   │   ├── Sidebar.jsx            # App sidebar navigation
│   │   ├── Header.jsx             # Top header with profile
│   │   └── Layout.jsx             # Main layout wrapper
│   │
│   ├── auth/
│   │   ├── LoginForm.jsx          # Login form
│   │   ├── SignupForm.jsx         # Signup form
│   │   └── GoogleAuthButton.jsx   # Google OAuth button
│   │
│   ├── accounts/
│   │   ├── AccountCard.jsx        # Single account display
│   │   ├── ConnectButton.jsx      # Platform connect button
│   │   └── AccountsList.jsx       # List of connected accounts
│   │
│   ├── create/
│   │   ├── ScriptGenerator.jsx    # Script generation form
│   │   ├── VoiceSelector.jsx      # Voice selection
│   │   ├── VisualSelector.jsx     # Visual selection
│   │   ├── VideoPreview.jsx       # Video preview player
│   │   └── PublishModal.jsx       # Publishing modal
│   │
│   ├── videos/
│   │   ├── VideoCard.jsx          # Single video card
│   │   ├── VideoList.jsx          # Video library list
│   │   └── VideoDetails.jsx       # Video details modal
│   │
│   ├── analytics/
│   │   ├── SummaryCards.jsx       # Dashboard summary cards
│   │   ├── PlatformChart.jsx      # Platform comparison chart
│   │   ├── PerformanceGraph.jsx   # Time-series graph
│   │   └── VideoMetricsTable.jsx  # Video metrics table
│   │
│   └── insights/
│       ├── RecommendationCard.jsx # AI recommendation display
│       └── InsightsPanel.jsx      # Insights dashboard
│
├── pages/
│   ├── Login.jsx                  # Login page
│   ├── Signup.jsx                 # Signup page
│   ├── Dashboard.jsx              # Dashboard home
│   ├── Accounts.jsx               # Connected accounts page
│   ├── CreateVideo.jsx            # Video creation page
│   ├── VideoLibrary.jsx           # Video library page
│   └── Analytics.jsx              # Analytics page
│
├── context/
│   ├── AuthContext.jsx            # Auth context provider
│   └── AppContext.jsx             # Global app state
│
├── hooks/
│   ├── useAuth.js                 # Auth hook
│   ├── useApi.js                  # API call hook
│   └── use-toast.js               # Toast notifications (pre-existing)
│
├── services/
│   └── api.js                     # API client (axios/fetch wrapper)
│
└── utils/
    ├── constants.js               # Frontend constants
    └── helpers.js                 # Utility functions
```

---

## 🔐 ENVIRONMENT VARIABLES (Backend .env)

```bash
# App Configuration
APP_ENV=development
SECRET_KEY=<generate-random-secret>
JWT_SECRET_KEY=<generate-random-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Database
MONGO_URL=<from-existing-env>
DB_NAME=autoshorts_ai

# OpenAI
OPENAI_API_KEY=

# Gemini
GEMINI_API_KEY=

# ElevenLabs
ELEVENLABS_API_KEY=

# YouTube OAuth
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=<user-needs-to-provide>
YOUTUBE_REDIRECT_URI=<backend-url>/api/platforms/youtube/callback

# Instagram OAuth (Meta)
INSTAGRAM_APP_ID=<user-needs-to-provide>
INSTAGRAM_APP_SECRET=<user-needs-to-provide>
INSTAGRAM_REDIRECT_URI=<backend-url>/api/platforms/instagram/callback

# Facebook OAuth
FACEBOOK_APP_ID=<user-needs-to-provide>
FACEBOOK_APP_SECRET=<user-needs-to-provide>
FACEBOOK_REDIRECT_URI=<backend-url>/api/platforms/facebook/callback

# Pexels (for stock footage)
PEXELS_API_KEY=<optional-free-key>

# Unsplash (for stock images)
UNSPLASH_ACCESS_KEY=<optional-free-key>

# File Storage
VIDEO_STORAGE_PATH=/app/backend/storage/videos
AUDIO_STORAGE_PATH=/app/backend/storage/audio
IMAGE_STORAGE_PATH=/app/backend/storage/images
TEMP_STORAGE_PATH=/app/backend/storage/temp

# FFmpeg
FFMPEG_PATH=/usr/bin/ffmpeg

# Background Workers
RENDER_WORKER_ENABLED=true
SCHEDULER_WORKER_ENABLED=true
```

---

## 🔄 DATA FLOW DIAGRAMS

### 1. **Video Creation Flow**
```
User Input (Platform, Niche, Language, Duration)
    ↓
[Content Generator Service]
    ↓ (calls OpenAI/Gemini)
Script Generated (Hook + Story + Ending)
    ↓
[TTS Generator Service]
    ↓ (calls ElevenLabs)
Audio File Created
    ↓
[Visual Generator Service]
    ↓ (calls OpenAI DALL-E / Pexels)
Images/Videos Fetched
    ↓
[Video Renderer Service]
    ↓ (FFmpeg processing in queue)
Final Video Rendered (9:16 format)
    ↓
Saved to Database & Storage
```

### 2. **Publishing Flow**
```
User Selects Video + Platform(s) + Account(s)
    ↓
[Publishing Service]
    ↓ (if scheduled)
[Scheduler Service] → Stores in schedules collection
    ↓ (at scheduled time OR instant)
[Platform Publisher] (YouTube/Instagram/Facebook)
    ↓ (OAuth token used)
Upload to Platform API
    ↓
Platform Video ID Returned
    ↓
Update videos.published_platforms
```

### 3. **Analytics Sync Flow**
```
[Background Worker] (runs every hour)
    ↓
Fetch all published videos from DB
    ↓
For each platform video:
    ↓
[Analytics Sync Service]
    ↓ (calls Platform Insights API)
Fetch Views, Likes, Comments, Shares
    ↓
Store in analytics collection
    ↓
Update metrics_history (time-series)
```

---

## 🎯 CRITICAL TECHNICAL DECISIONS

### 1. **Video Rendering Strategy**
- **Approach**: Queue-based background processing
- **Why**: Video rendering is CPU-intensive and can take 1-3 minutes
- **Implementation**: 
  - Create render job in `render_queue` collection
  - Background worker picks up pending jobs
  - Frontend polls `/api/videos/render/{job_id}/status` for progress

### 2. **Token Storage & Security**
- **Challenge**: OAuth tokens must be stored securely
- **Solution**: 
  - Encrypt tokens using Fernet (symmetric encryption)
  - Store encryption key in environment variable
  - Never expose tokens in API responses

### 3. **Multi-Platform Publishing**
- **Challenge**: Different platforms have different APIs and requirements
- **Solution**: 
  - Abstract publisher interface
  - Platform-specific implementations (YouTube/Instagram/Facebook)
  - Common error handling and retry logic

### 4. **Analytics Time-Series Data**
- **Challenge**: Need historical performance tracking
- **Solution**: 
  - Store daily metrics in `metrics_history` array
  - Background job syncs every hour
  - Frontend can graph trends over time

### 5. **AI Model Selection**
- **Primary**: OpenAI (user has key)
- **Fallback**: Gemini (user has key)
- **Strategy**: Try primary, fallback on error

---

## 🚀 DEPLOYMENT CONSIDERATIONS (For Later)

### Backend Hosting Options
- Render.com (free tier available)
- Railway.app (free tier with limits)
- Heroku (paid)

### Frontend Hosting
- Vercel (free tier, automatic deployments)
- Netlify (free tier)

### Database
- MongoDB Atlas (free 512MB cluster)
- Or use existing MongoDB in Kubernetes cluster

### File Storage (Future)
- AWS S3 (for production)
- Cloudinary (for videos/images)
- Currently: Local storage in `/app/backend/storage/`

### Background Workers
- Supervisor (already available in environment)
- Celery (for more complex job management - future)

---

## ✅ ARCHITECTURE VALIDATION CHECKLIST

- [x] Modular service architecture (easy to test/maintain)
- [x] Clear separation of concerns (routes → services → database)
- [x] Scalable queue-based video rendering
- [x] Secure OAuth token management
- [x] Time-series analytics storage
- [x] Background workers for async tasks
- [x] Multi-platform abstraction layer
- [x] Comprehensive API endpoint structure
- [x] Proper database indexing strategy
- [x] Error handling and logging strategy

---

**This architecture is production-ready and follows industry best practices for SaaS platforms.**
