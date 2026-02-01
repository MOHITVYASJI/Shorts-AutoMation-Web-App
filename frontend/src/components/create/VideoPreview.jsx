// import React, { useState, useEffect } from 'react';
// import { Button } from '@/components/ui/button';
// import { Card } from '@/components/ui/card';
// import { Progress } from '@/components/ui/progress';
// import { Loader2, Video, Download, Upload, Play } from 'lucide-react';
// import { toast } from 'sonner';
// import axios from 'axios';
// import { useAuth } from '@/context/AuthContext';

// const API_URL = process.env.REACT_APP_BACKEND_URL;

// const VideoPreview = ({ script, voice, visuals, onVideoRendered, onPublish, videoFile }) => {
//   const { token } = useAuth();
//   const [rendering, setRendering] = useState(false);
//   const [renderProgress, setRenderProgress] = useState(0);
//   const [jobId, setJobId] = useState(null);
//   const [renderedVideo, setRenderedVideo] = useState(videoFile || null);

//   useEffect(() => {
//     let interval;
//     if (jobId && rendering) {
//       interval = setInterval(() => {
//         checkRenderStatus();
//       }, 2000);
//     }
//     return () => clearInterval(interval);
//   }, [jobId, rendering]);

//   const handleRenderVideo = async () => {
//     setRendering(true);
//     setRenderProgress(10);

//     try {
//       const response = await axios.post(
//         `${API_URL}/api/videos/render`,
//         {
//           script,
//           voice_url: voice?.audio_url,
//           visuals: visuals.map(v => v.url),
//           captions_enabled: true,
//           background_music: true
//         },
//         {
//           headers: { Authorization: `Bearer ${token}` }
//         }
//       );

//       setJobId(response.data.job_id);
//       toast.success('Video rendering started!');
//     } catch (error) {
//       console.error('Error starting render:', error);
//       toast.error(error.response?.data?.detail || 'Failed to start rendering');
//       setRendering(false);
//     }
//   };

//   const checkRenderStatus = async () => {
//     try {
//       const response = await axios.get(
//         `${API_URL}/api/videos/render/${jobId}/status`,
//         {
//           headers: { Authorization: `Bearer ${token}` }
//         }
//       );

//       const { status, progress, output_file_path } = response.data;
//       setRenderProgress(progress || 0);

//       if (status === 'completed') {
//         setRendering(false);
//         setRenderedVideo({
//           path: output_file_path,
//           url: `${API_URL}/api/videos/render/${jobId}/download`
//         });
//         toast.success('Video rendered successfully!');
//         onVideoRendered(jobId, {
//           path: output_file_path,
//           url: `${API_URL}/api/videos/render/${jobId}/download`
//         });
//       } else if (status === 'failed') {
//         setRendering(false);
//         toast.error('Video rendering failed');
//       }
//     } catch (error) {
//       console.error('Error checking render status:', error);
//     }
//   };

//   const handleDownload = () => {
//     if (renderedVideo?.url) {
//       window.open(renderedVideo.url, '_blank');
//     }
//   };

//   return (
//     <div className="space-y-6" data-testid="video-preview">
//       <Card className="p-6 bg-slate-800/30 border-slate-700">
//         <div className="space-y-4">
//           <h3 className="text-white font-medium">Content Summary</h3>
          
//           <div className="space-y-3">
//             <div className="p-3 bg-slate-800 rounded-lg">
//               <p className="text-xs text-slate-400">Title</p>
//               <p className="text-white text-sm mt-1">{script?.title}</p>
//             </div>

//             <div className="p-3 bg-slate-800 rounded-lg">
//               <p className="text-xs text-slate-400">Script Length</p>
//               <p className="text-white text-sm mt-1">
//                 {script?.hook?.split(' ').length + script?.story?.split(' ').length} words
//               </p>
//             </div>

//             <div className="p-3 bg-slate-800 rounded-lg">
//               <p className="text-xs text-slate-400">Voice Duration</p>
//               <p className="text-white text-sm mt-1">{voice?.duration || 0}s</p>
//             </div>

//             <div className="p-3 bg-slate-800 rounded-lg">
//               <p className="text-xs text-slate-400">Visuals</p>
//               <p className="text-white text-sm mt-1">{visuals?.length || 0} images selected</p>
//             </div>
//           </div>
//         </div>
//       </Card>

//       {!renderedVideo ? (
//         <div className="space-y-4">
//           {rendering && (
//             <Card className="p-6 bg-slate-800/30 border-slate-700">
//               <div className="space-y-3">
//                 <div className="flex items-center justify-between">
//                   <p className="text-white">Rendering video...</p>
//                   <p className="text-slate-400 text-sm">{renderProgress}%</p>
//                 </div>
//                 <Progress value={renderProgress} className="w-full" />
//               </div>
//             </Card>
//           )}

//           <Button
//             onClick={handleRenderVideo}
//             disabled={rendering}
//             className="w-full bg-indigo-600 hover:bg-indigo-700"
//             data-testid="render-video-button"
//           >
//             {rendering ? (
//               <>
//                 <Loader2 className="w-4 h-4 mr-2 animate-spin" />
//                 Rendering... {renderProgress}%
//               </>
//             ) : (
//               <>
//                 <Video className="w-4 h-4 mr-2" />
//                 Render Video
//               </>
//             )}
//           </Button>
//         </div>
//       ) : (
//         <div className="space-y-4">
//           <Card className="p-6 bg-slate-800/30 border-slate-700">
//             <div className="space-y-4">
//               <div className="flex items-center justify-between">
//                 <div>
//                   <h3 className="text-white font-medium">Video Ready!</h3>
//                   <p className="text-sm text-slate-400">Your video has been rendered successfully</p>
//                 </div>
//                 <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center">
//                   <Play className="w-6 h-6 text-green-400" />
//                 </div>
//               </div>

//               <div className="aspect-[9/16] bg-slate-900 rounded-lg flex items-center justify-center">
//                 <Video className="w-16 h-16 text-slate-600" />
//                 <p className="text-slate-500 ml-3">Video preview</p>
//               </div>
//             </div>
//           </Card>

//           <div className="grid grid-cols-2 gap-3">
//             <Button
//               onClick={handleDownload}
//               variant="outline"
//               className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
//               data-testid="download-video-button"
//             >
//               <Download className="w-4 h-4 mr-2" />
//               Download
//             </Button>
//             <Button
//               onClick={onPublish}
//               className="bg-indigo-600 hover:bg-indigo-700"
//               data-testid="publish-video-button"
//             >
//               <Upload className="w-4 h-4 mr-2" />
//               Publish
//             </Button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default VideoPreview;
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Loader2, Video, Download, Upload } from 'lucide-react';
import { toast } from 'sonner';
import { videosAPI } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VideoPreview = ({ script, voice, visuals, onVideoRendered, onPublish, videoFile }) => {
  const { token } = useAuth();
  const [rendering, setRendering] = useState(false);
  const [renderedVideo, setRenderedVideo] = useState(videoFile || null);

  const handleRenderVideo = async () => {
    if (!script || !voice || !visuals || visuals.length === 0) {
      toast.error('Missing required content. Please complete all previous steps.');
      return;
    }

    setRendering(true);
    try {
      // Prepare render request
      const renderRequest = {
        audio_path: voice.audio_path,
        image_paths: visuals.map(v => v.path || v.url),
        duration: voice.duration || 30,
        add_captions: false,
        script: script,
        title: script.title || 'Untitled Video',
        description: script.description || '',
        hashtags: Array.isArray(script.hashtags) ? script.hashtags : [],
        niche: script.niche || 'general'
      };

      const response = await videosAPI.renderVideo(renderRequest);

      const videoData = {
        video_id: response.video_id,
        path: response.video_path,
        url: `${API_URL}/api/videos/${response.video_id}/download`
      };

      setRenderedVideo(videoData);
      toast.success('Video rendered successfully!');
      onVideoRendered(response.video_id, videoData);
    } catch (error) {
      console.error('Error rendering video:', error);
      toast.error(error.response?.data?.detail || 'Failed to render video');
    } finally {
      setRendering(false);
    }
  };

  const handleDownload = () => {
    if (renderedVideo?.url) {
      window.open(renderedVideo.url, '_blank');
      toast.success('Download started');
    }
  };

  return (
    <div className="space-y-6" data-testid="video-preview">
      <Card className="p-6 bg-slate-800/30 border-slate-700">
        <div className="space-y-4">
          <h3 className="text-white font-medium text-lg">Content Summary</h3>
          
          <div className="space-y-3">
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400">Title</p>
              <p className="text-white text-sm mt-1">{script?.title || 'Untitled'}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-800 rounded-lg">
                <p className="text-xs text-slate-400">Platform</p>
                <p className="text-white text-sm mt-1 capitalize">{script?.platform || 'YouTube'}</p>
              </div>

              <div className="p-3 bg-slate-800 rounded-lg">
                <p className="text-xs text-slate-400">Niche</p>
                <p className="text-white text-sm mt-1 capitalize">{script?.niche?.replace('_', ' ') || 'General'}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-800 rounded-lg">
                <p className="text-xs text-slate-400">Voice Duration</p>
                <p className="text-white text-sm mt-1">{voice?.duration || 0}s</p>
              </div>

              <div className="p-3 bg-slate-800 rounded-lg">
                <p className="text-xs text-slate-400">Visuals</p>
                <p className="text-white text-sm mt-1">{visuals?.length || 0} images</p>
              </div>
            </div>

            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400">Hashtags</p>
              <p className="text-white text-sm mt-1">
                {Array.isArray(script?.hashtags) ? script.hashtags.join(' ') : (script?.hashtags || 'None')}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {!renderedVideo ? (
        <Button
          onClick={handleRenderVideo}
          disabled={rendering}
          className="w-full bg-indigo-600 hover:bg-indigo-700 py-6 text-lg"
          data-testid="render-video-button"
        >
          {rendering ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Rendering Video...
            </>
          ) : (
            <>
              <Video className="w-5 h-5 mr-2" />
              Render Video
            </>
          )}
        </Button>
      ) : (
        <div className="space-y-4">
          <Card className="p-6 bg-green-500/10 border-green-500/30">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                  <Video className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Video Ready!</h3>
                  <p className="text-sm text-slate-400">Your video has been rendered successfully</p>
                </div>
              </div>

              <div className="p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400">Video ID</p>
                <p className="text-white text-sm mt-1 font-mono">{renderedVideo.video_id}</p>
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={handleDownload}
              variant="outline"
              className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700 py-6"
              data-testid="download-video-button"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
            <Button
              onClick={onPublish}
              className="bg-indigo-600 hover:bg-indigo-700 py-6"
              data-testid="publish-video-button"
            >
              <Upload className="w-4 h-4 mr-2" />
              Publish
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPreview;