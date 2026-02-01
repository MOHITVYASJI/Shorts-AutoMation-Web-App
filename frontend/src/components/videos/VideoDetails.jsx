import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Video, Download, Trash2, Eye, ThumbsUp, Share2, ExternalLink, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VideoDetails = ({ video, open, onClose, onVideoDeleted, onVideoUpdated }) => {
  const { token } = useAuth();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`${API_URL}/api/videos/${video.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      onVideoDeleted(video.id);
    } catch (error) {
      console.error('Error deleting video:', error);
      toast.error('Failed to delete video');
    } finally {
      setDeleting(false);
      setShowDeleteDialog(false);
    }
  };

  const handleDownload = () => {
    if (video.video_file_path) {
      window.open(`${API_URL}/api/videos/${video.id}/download`, '_blank');
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

  const getTotalShares = () => {
    if (!video.analytics) return 0;
    return video.analytics.reduce((sum, a) => sum + (a.shares || 0), 0);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="bg-slate-900 border-slate-800 max-w-4xl max-h-[90vh] overflow-y-auto" data-testid="video-details-modal">
          <DialogHeader>
            <DialogTitle className="text-white">{video.title || 'Untitled Video'}</DialogTitle>
            <DialogDescription className="text-slate-400">
              Created on {format(new Date(video.created_at), 'PPP')}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800">
              <TabsTrigger value="overview" className="data-[state=active]:bg-indigo-600">Overview</TabsTrigger>
              <TabsTrigger value="content" className="data-[state=active]:bg-indigo-600">Content</TabsTrigger>
              <TabsTrigger value="analytics" className="data-[state=active]:bg-indigo-600">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4 mt-4">
              {/* Video Preview */}
              <div className="aspect-[9/16] max-w-sm mx-auto bg-slate-800 rounded-lg overflow-hidden">
                {video.thumbnail_path ? (
                  <img src={video.thumbnail_path} alt={video.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Video className="w-16 h-16 text-slate-600" />
                  </div>
                )}
              </div>

              {/* Stats */}
              {video.status === 'published' && (
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-800 rounded-lg text-center">
                    <Eye className="w-6 h-6 text-indigo-400 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{getTotalViews().toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Views</p>
                  </div>
                  <div className="p-4 bg-slate-800 rounded-lg text-center">
                    <ThumbsUp className="w-6 h-6 text-green-400 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{getTotalLikes().toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Likes</p>
                  </div>
                  <div className="p-4 bg-slate-800 rounded-lg text-center">
                    <Share2 className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{getTotalShares().toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Shares</p>
                  </div>
                </div>
              )}

              {/* Published Platforms */}
              {video.published_platforms && video.published_platforms.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-white font-medium">Published On</h4>
                  <div className="space-y-2">
                    {video.published_platforms.map((pub, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                        <div>
                          <p className="text-white capitalize">{pub.platform}</p>
                          <p className="text-xs text-slate-400">
                            {format(new Date(pub.published_at), 'PPp')}
                          </p>
                        </div>
                        {pub.url && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => window.open(pub.url, '_blank')}
                            className="text-indigo-400 hover:text-indigo-300"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="content" className="space-y-4 mt-4">
              <div className="space-y-4">
                <div>
                  <h4 className="text-white font-medium mb-2">Description</h4>
                  <p className="text-slate-300 p-3 bg-slate-800 rounded-lg">
                    {video.description || 'No description'}
                  </p>
                </div>

                {video.script && (
                  <>
                    <div>
                      <h4 className="text-white font-medium mb-2">Hook</h4>
                      <p className="text-slate-300 p-3 bg-slate-800 rounded-lg">
                        {video.script.hook}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-white font-medium mb-2">Story</h4>
                      <p className="text-slate-300 p-3 bg-slate-800 rounded-lg">
                        {video.script.story}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-white font-medium mb-2">Ending</h4>
                      <p className="text-slate-300 p-3 bg-slate-800 rounded-lg">
                        {video.script.ending}
                      </p>
                    </div>
                  </>
                )}

                {video.hashtags && video.hashtags.length > 0 && (
                  <div>
                    <h4 className="text-white font-medium mb-2">Hashtags</h4>
                    <div className="flex flex-wrap gap-2">
                      {video.hashtags.map((tag, idx) => (
                        <Badge key={idx} variant="outline" className="border-slate-700">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4 mt-4">
              {video.analytics && video.analytics.length > 0 ? (
                <div className="space-y-3">
                  {video.analytics.map((analytic, idx) => (
                    <div key={idx} className="p-4 bg-slate-800 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-white font-medium capitalize">{analytic.platform}</h4>
                        <Badge variant="outline" className="border-slate-700">
                          {format(new Date(analytic.last_synced_at || analytic.created_at), 'PPp')}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-4 gap-3">
                        <div>
                          <p className="text-xs text-slate-400">Views</p>
                          <p className="text-lg font-bold text-white">{(analytic.views || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400">Likes</p>
                          <p className="text-lg font-bold text-white">{(analytic.likes || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400">Comments</p>
                          <p className="text-lg font-bold text-white">{(analytic.comments || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400">Shares</p>
                          <p className="text-lg font-bold text-white">{(analytic.shares || 0).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-slate-400">No analytics available yet</p>
                  <p className="text-sm text-slate-500 mt-2">
                    Analytics will appear once your video is published
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>

          {/* Actions */}
          <div className="flex gap-3 mt-6">
            <Button
              onClick={handleDownload}
              variant="outline"
              className="flex-1 bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
              disabled={!video.video_file_path}
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
            <Button
              onClick={() => setShowDeleteDialog(true)}
              variant="destructive"
              className="flex-1"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="bg-slate-900 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Delete Video?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Are you sure you want to delete <span className="text-white font-medium">{video.title}</span>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-800 text-white hover:bg-slate-700 border-slate-700">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default VideoDetails;