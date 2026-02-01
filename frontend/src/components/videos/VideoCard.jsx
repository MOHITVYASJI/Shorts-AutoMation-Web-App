import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Video, Clock, Eye, ThumbsUp } from 'lucide-react';
import { format } from 'date-fns';

const VideoCard = ({ video, onClick }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'published':
        return 'bg-green-500/10 text-green-400';
      case 'rendering':
        return 'bg-yellow-500/10 text-yellow-400';
      case 'draft':
        return 'bg-slate-500/10 text-slate-400';
      default:
        return 'bg-slate-500/10 text-slate-400';
    }
  };

  const getTotalViews = () => {
    if (!video.analytics) return 0;
    return video.analytics.reduce((sum, a) => sum + (a.views || 0), 0);
  };

  const getTotalLikes = () => {
    if (!video.analytics) return 0;
    return video.analytics.reduce((sum, a) => sum + (a.likes || 0), 0);
  };

  return (
    <Card
      onClick={onClick}
      className="border-slate-800 bg-slate-900/50 backdrop-blur-sm hover:border-slate-700 transition-all cursor-pointer group"
      data-testid="video-card"
    >
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Thumbnail */}
          <div className="aspect-[9/16] bg-slate-800 rounded-lg overflow-hidden relative">
            {video.thumbnail_path ? (
              <img
                src={video.thumbnail_path}
                alt={video.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Video className="w-12 h-12 text-slate-600" />
              </div>
            )}
            <div className="absolute top-2 right-2">
              <Badge className={getStatusColor(video.status)}>
                {video.status}
              </Badge>
            </div>
          </div>

          {/* Info */}
          <div>
            <h3 className="text-white font-medium line-clamp-2 group-hover:text-indigo-400 transition-colors">
              {video.title || 'Untitled Video'}
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              {video.niche && `${video.niche.replace('_', ' ')} • `}
              {format(new Date(video.created_at), 'MMM d, yyyy')}
            </p>
          </div>

          {/* Stats */}
          {video.status === 'published' && (
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <div className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                <span>{getTotalViews().toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <ThumbsUp className="w-4 h-4" />
                <span>{getTotalLikes().toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{video.duration || 0}s</span>
              </div>
            </div>
          )}

          {/* Platforms */}
          {video.published_platforms && video.published_platforms.length > 0 && (
            <div className="flex gap-2">
              {video.published_platforms.map((pub, idx) => (
                <Badge key={idx} variant="outline" className="text-xs border-slate-700">
                  {pub.platform}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default VideoCard;