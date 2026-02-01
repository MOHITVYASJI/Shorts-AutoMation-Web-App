# 🎬 AutoShorts AI - Phase-Wise Development TODO

## 📋 PROJECT CONTEXT
- **Product**: AI-powered Multi-Platform Short Video Automation & Analytics Platform
- **MVP Scope**: YouTube Shorts + Instagram Reels + Facebook Reels
- **Tech Stack**: React + FastAPI + MongoDB + FFmpeg + AI APIs
- **User Provided**: OpenAI, Gemini, ElevenLabs API keys + YouTube OAuth Client ID

---

## 🏗️ PHASE 0: PLANNING & ARCHITECTURE SETUP

### 0.1 Tech Stack Confirmation ✅
- [x] Frontend: React + Tailwind CSS + Recharts
- [x] Backend: FastAPI (Python)
- [x] Database: MongoDB
- [x] AI Services: OpenAI GPT + Gemini
- [x] TTS: ElevenLabs (primary) + Open-source fallback
- [x] Video: FFmpeg + AI images + Stock footage
- [x] Platforms: YouTube, Instagram, Facebook APIs

### 0.2 High-Level Architecture Design
- [ ] Define microservices architecture
  - Auth Service
  - Content Generation Service
  - Video Rendering Service (queue-based)
  - Publishing Service
  - Analytics Service
- [ ] Design database schema
  - Users collection
  - ConnectedAccounts collection
  - Videos collection
  - Analytics collection
  - RenderQueue collection
- [ ] Define API endpoints structure
- [ ] Plan file storage strategy (videos, images, temp files)

### 0.3 Repository Structure Setup
- [ ] Create modular backend folder structure
- [ ] Create frontend component architecture
- [ ] Setup environment variables template
- [ ] Create README with setup instructions

---

## 🚀 PHASE 1: MVP CORE (AUTH + YOUTUBE INTEGRATION)

### 1.1 Backend Setup
- [ ] Install required Python packages
  - fastapi, uvicorn
  - pymongo, motor (async MongoDB)
  - python-jose[cryptography] (JWT)
  - passlib[bcrypt] (password hashing)
  - google-auth, google-auth-oauthlib, google-api-python-client
  - openai, google-generativeai
  - elevenlabs
  - ffmpeg-python
  - httpx, aiofiles
- [ ] Update requirements.txt with all dependencies
- [ ] Create .env template with all API keys
- [ ] Setup MongoDB connection utility

### 1.2 Authentication Module
- [ ] Design User schema (MongoDB model)
- [ ] Implement signup endpoint (`POST /api/auth/signup`)
- [ ] Implement login endpoint (`POST /api/auth/login`)
- [ ] Implement Google OAuth login (`POST /api/auth/google`)
- [ ] JWT token generation & validation middleware
- [ ] User profile endpoints (`GET/PUT /api/auth/profile`)

### 1.3 YouTube Account Integration
- [ ] Create ConnectedAccounts schema
- [ ] YouTube OAuth 2.0 flow endpoints
  - `GET /api/platforms/youtube/auth-url` (generate OAuth URL)
  - `POST /api/platforms/youtube/callback` (handle OAuth callback)
  - `GET /api/platforms/youtube/accounts` (list connected accounts)
  - `DELETE /api/platforms/youtube/accounts/{id}` (disconnect account)
- [ ] Store YouTube tokens securely (encrypted)
- [ ] Token refresh logic

### 1.4 Frontend - Auth UI
- [ ] Create login page component
- [ ] Create signup page component
- [ ] Google OAuth button integration
- [ ] JWT storage in localStorage
- [ ] Protected route wrapper
- [ ] User context provider

### 1.5 Frontend - Dashboard Layout
- [ ] Create main dashboard layout
- [ ] Sidebar navigation
- [ ] Top header with user profile
- [ ] Routing setup (React Router)
  - `/dashboard` - Home
  - `/accounts` - Connected accounts
  - `/create` - Video creation
  - `/videos` - Video library
  - `/analytics` - Analytics

### 1.6 Frontend - Account Integration UI
- [ ] Connected accounts page
- [ ] YouTube connect button
- [ ] OAuth popup/redirect handler
- [ ] Account list with status indicators
- [ ] Disconnect account functionality

---

## 🤖 PHASE 2: AI CONTENT ENGINE

### 2.1 Content Generation Backend
- [ ] Create content generation service (`/backend/services/content_generator.py`)
- [ ] Implement script generation endpoint
  - `POST /api/content/generate-script`
  - Input: platform, niche, language, duration
  - Output: hook, story, ending, title, description, hashtags
- [ ] OpenAI integration (primary)
- [ ] Gemini integration (fallback)
- [ ] Prompt engineering for viral hooks
- [ ] Niche-specific prompt templates

### 2.2 TTS (Text-to-Speech) Integration
- [ ] Create TTS service (`/backend/services/tts_generator.py`)
- [ ] ElevenLabs API integration (primary)
- [ ] Open-source TTS fallback (gTTS or pyttsx3)
- [ ] Voice generation endpoint
  - `POST /api/content/generate-voice`
  - Input: text, voice_id, language
  - Output: audio file path

### 2.3 Visual Content Service
- [ ] Create visual service (`/backend/services/visual_generator.py`)
- [ ] AI image generation integration
  - OpenAI DALL-E integration
  - Gemini Nano Banana integration
- [ ] Stock footage/image fetcher (Pexels/Unsplash API)
- [ ] Image selection endpoint
  - `POST /api/content/generate-visuals`
  - Input: script, niche, style
  - Output: list of image/video URLs

### 2.4 Frontend - Content Creation UI
- [ ] Create video generation form
  - Platform selector (YouTube/Instagram/Facebook)
  - Niche dropdown
  - Language selector
  - Duration slider (10-60 seconds)
- [ ] Generate script button
- [ ] Script preview & edit area
- [ ] Voice preview player
- [ ] Visual preview gallery
- [ ] Regenerate options for each component

---

## 🎬 PHASE 3: VIDEO RENDERING ENGINE

### 3.1 Video Rendering Service
- [ ] Create video renderer (`/backend/services/video_renderer.py`)
- [ ] FFmpeg integration
- [ ] Video composition logic
  - Combine visuals (images/videos)
  - Add voiceover audio
  - Add background music
  - Generate auto captions (using Whisper or subtitle lib)
  - Apply 9:16 aspect ratio
  - Add loop-compatible ending
- [ ] Render queue system (use MongoDB for job queue)
- [ ] Background worker for rendering
- [ ] Progress tracking

### 3.2 Video Rendering Endpoints
- [ ] Create render job endpoint
  - `POST /api/video/render`
  - Input: script, voice_url, visuals, music, captions_enabled
  - Output: job_id
- [ ] Check render status endpoint
  - `GET /api/video/render/{job_id}/status`
  - Output: status (pending/processing/completed/failed), progress %
- [ ] Download rendered video endpoint
  - `GET /api/video/render/{job_id}/download`

### 3.3 Video Storage & Management
- [ ] Create Videos schema (MongoDB)
  - video_id, user_id, title, description, hashtags
  - file_path, thumbnail_path, duration
  - platform, niche, language
  - created_at, status (draft/published)
- [ ] Video library endpoints
  - `GET /api/videos` (list user videos)
  - `GET /api/videos/{id}` (get single video)
  - `DELETE /api/videos/{id}` (delete video)
  - `PUT /api/videos/{id}` (update metadata)

### 3.4 Frontend - Video Creation Workflow
- [ ] Create step-by-step wizard UI
  - Step 1: Generate script
  - Step 2: Generate voice & visuals
  - Step 3: Review & customize
  - Step 4: Render video
- [ ] Render progress indicator
- [ ] Video preview player
- [ ] Download video button (for local backup)

---

## 📤 PHASE 4: PUBLISHING & SCHEDULING

### 4.1 YouTube Upload Service
- [ ] Create YouTube upload service (`/backend/services/youtube_publisher.py`)
- [ ] YouTube API upload implementation
  - Video upload with title, description, tags
  - Visibility control (public/private/unlisted)
  - Category & language settings
- [ ] Upload endpoint
  - `POST /api/publish/youtube`
  - Input: video_id, account_id, metadata, publish_time (optional)

### 4.2 Instagram Upload Service
- [ ] Create Instagram service (`/backend/services/instagram_publisher.py`)
- [ ] Instagram Graph API integration
  - Media upload (Reels)
  - Caption & hashtags
- [ ] Upload endpoint
  - `POST /api/publish/instagram`

### 4.3 Facebook Upload Service
- [ ] Create Facebook service (`/backend/services/facebook_publisher.py`)
- [ ] Facebook Graph API integration
  - Video upload to Page
  - Description & tags
- [ ] Upload endpoint
  - `POST /api/publish/facebook`

### 4.4 Scheduling System
- [ ] Create Scheduler service
- [ ] Schedule schema (MongoDB)
  - video_id, platform, account_id, scheduled_time, status
- [ ] Background job processor (checks every minute)
- [ ] Schedule endpoints
  - `POST /api/publish/schedule` (schedule upload)
  - `GET /api/publish/schedule` (list scheduled uploads)
  - `DELETE /api/publish/schedule/{id}` (cancel schedule)

### 4.5 Frontend - Publishing UI
- [ ] Publish modal component
- [ ] Platform multi-select
- [ ] Account selector per platform
- [ ] Metadata editor (title, description, hashtags)
- [ ] Schedule date/time picker
- [ ] Instant publish button
- [ ] Publishing progress indicator
- [ ] Success/failure notifications

---

## 📊 PHASE 5: ANALYTICS & DASHBOARD

### 5.1 Analytics Data Collection
- [ ] Create analytics sync service (`/backend/services/analytics_sync.py`)
- [ ] YouTube Analytics API integration
  - Fetch views, likes, comments, shares
  - Retention data (if available)
- [ ] Instagram Insights API integration
- [ ] Facebook Insights API integration
- [ ] Analytics schema (MongoDB)
  - video_id, platform, account_id, date
  - views, likes, comments, shares, retention
- [ ] Background sync job (runs every hour)
- [ ] Sync endpoints
  - `POST /api/analytics/sync` (manual sync trigger)
  - `GET /api/analytics/video/{video_id}` (get video analytics)

### 5.2 Global Dashboard Backend
- [ ] Dashboard summary endpoint
  - `GET /api/dashboard/summary`
  - Output: total_uploads, total_views, best_platform, upload_calendar
- [ ] Platform-wise stats endpoint
  - `GET /api/dashboard/platform-stats`
  - Output: views/likes/shares per platform
- [ ] Best performing videos endpoint
  - `GET /api/dashboard/top-videos`

### 5.3 Account-Level Analytics Backend
- [ ] Account analytics endpoint
  - `GET /api/analytics/account/{account_id}`
  - Output: video list with metrics, time-series data

### 5.4 Frontend - Dashboard Home
- [ ] Summary cards
  - Total uploads
  - Total views
  - Best performing platform
  - Growth trend
- [ ] Upload calendar widget
- [ ] Recent videos table
- [ ] Quick action buttons

### 5.5 Frontend - Analytics Page
- [ ] Platform comparison charts (Recharts)
- [ ] Time-series performance graph
- [ ] Video performance table (sortable)
- [ ] Filter by date range, platform, niche
- [ ] Export analytics data (CSV)

---

## 🧠 PHASE 6: AI INSIGHTS ENGINE (ADVANCED)

### 6.1 Insights Service Backend
- [ ] Create insights analyzer (`/backend/services/insights_engine.py`)
- [ ] Analyze past performance patterns
  - Best upload time analysis
  - Best performing niche
  - Hook effectiveness analysis
  - Visual style performance
- [ ] Generate actionable suggestions
- [ ] Insights endpoint
  - `GET /api/insights/recommendations`
  - Output: list of AI-generated suggestions

### 6.2 Frontend - Insights Section
- [ ] Insights dashboard widget
- [ ] Recommendation cards
- [ ] Apply suggestion button (pre-fill creation form)

---

## 🔧 PHASE 7: POLISH & OPTIMIZATION

### 7.1 Error Handling & Validation
- [ ] Comprehensive error handling in all endpoints
- [ ] Input validation (Pydantic models)
- [ ] User-friendly error messages
- [ ] Rate limiting on API endpoints

### 7.2 Security Enhancements
- [ ] Encrypt stored OAuth tokens
- [ ] API key validation
- [ ] CORS configuration
- [ ] SQL injection prevention (using MongoDB properly)

### 7.3 Performance Optimization
- [ ] Database indexing
- [ ] API response caching (Redis optional)
- [ ] Video file cleanup (delete temp files)
- [ ] Pagination for video lists

### 7.4 UI/UX Polish
- [ ] Loading states for all async actions
- [ ] Toast notifications (success/error)
- [ ] Responsive design (mobile-friendly)
- [ ] Dark mode toggle
- [ ] Empty states for lists
- [ ] Tooltips and help text

### 7.5 Testing
- [ ] Backend API testing (manual curl tests)
- [ ] Frontend E2E testing (screenshot validation)
- [ ] Integration testing (YouTube upload flow)
- [ ] Error scenario testing

---

## 🚢 PHASE 8: DEPLOYMENT PREPARATION

### 8.1 Environment Configuration
- [ ] Production .env setup guide
- [ ] Secrets management strategy
- [ ] Database backup strategy

### 8.2 Documentation
- [ ] API documentation (endpoints, request/response)
- [ ] User guide (how to connect accounts, create videos)
- [ ] Troubleshooting guide

### 8.3 Monitoring & Logging
- [ ] Backend logging setup
- [ ] Error tracking
- [ ] Usage analytics

---

## 📝 NEXT STEPS (AFTER TODO COMPLETION)

### Immediate Next Actions:
1. Start with **PHASE 0.2**: Design database schemas in `/app/backend/models/`
2. Create initial file structure for backend services
3. Setup environment variables in `/app/backend/.env`
4. Install required packages and update requirements.txt

### Continuation Strategy:
- Work in small increments (1-2 tasks at a time)
- Test each module before moving to next
- Use testing subagent after completing each phase
- Create checkpoints after each major feature

---

## ⚠️ IMPORTANT NOTES

1. **API Keys Storage**: All provided API keys will be stored in `/app/backend/.env`
2. **OAuth Flow**: YouTube OAuth Client ID will be used for account connection
3. **Video Storage**: Videos will be stored in `/app/backend/storage/videos/`
4. **Queue Processing**: Use background workers for video rendering (avoid blocking)
5. **Platform Priority**: YouTube → Instagram → Facebook (in order of implementation)
6. **Testing**: Call testing subagent after each phase completion
7. **Database**: Use existing MongoDB connection from environment

---

## 🎯 SUCCESS CRITERIA

- [ ] User can signup/login
- [ ] User can connect YouTube/Instagram/Facebook accounts
- [ ] User can generate AI scripts
- [ ] User can render short videos (9:16 aspect ratio)
- [ ] User can publish/schedule videos to multiple platforms
- [ ] User can view analytics in centralized dashboard
- [ ] System generates AI-powered improvement suggestions

---

**TOTAL ESTIMATED TASKS**: ~150 granular tasks across 8 phases
**CRITICAL PATH**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (Phases 5-8 can be parallel)
