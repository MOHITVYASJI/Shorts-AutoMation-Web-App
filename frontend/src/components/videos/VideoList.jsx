import React from 'react';
import VideoCard from './VideoCard';

const VideoList = ({ videos, onVideoClick }) => {
  if (!videos || videos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">No videos found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map(video => (
        <VideoCard
          key={video.id}
          video={video}
          onClick={() => onVideoClick(video)}
        />
      ))}
    </div>
  );
};

export default VideoList;