import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Youtube, Instagram, Facebook, Loader2, Upload, CalendarIcon, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { format } from 'date-fns';
import { Alert, AlertDescription } from '@/components/ui/alert';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PublishModal = ({ open, onClose, videoFile, scriptData }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [scheduleDate, setScheduleDate] = useState(null);
  const [scheduleTime, setScheduleTime] = useState('');
  const [metadata, setMetadata] = useState({
    title: scriptData?.title || '',
    description: scriptData?.description || '',
    hashtags: scriptData?.hashtags?.join(' ') || ''
  });

  useEffect(() => {
    if (open) {
      fetchAccounts();
    }
  }, [open]);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/platforms/accounts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAccounts(response.data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      toast.error('Failed to load connected accounts');
    }
  };

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'text-pink-500',
      bgColor: 'bg-pink-500/10'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10'
    }
  ];

  const togglePlatform = (platformId) => {
    if (selectedPlatforms.includes(platformId)) {
      setSelectedPlatforms(selectedPlatforms.filter(p => p !== platformId));
    } else {
      setSelectedPlatforms([...selectedPlatforms, platformId]);
    }
  };

  const isPlatformConnected = (platformId) => {
    return accounts.some(acc => acc.platform === platformId && acc.status === 'active');
  };

  const handlePublish = async (isScheduled = false) => {
    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    // Check if selected platforms are connected
    const unconnectedPlatforms = selectedPlatforms.filter(p => !isPlatformConnected(p));
    if (unconnectedPlatforms.length > 0) {
      toast.error(`Please connect ${unconnectedPlatforms.join(', ')} first`);
      return;
    }

    if (isScheduled && (!scheduleDate || !scheduleTime)) {
      toast.error('Please select date and time for scheduling');
      return;
    }

    setLoading(true);
    try {
      const publishData = {
        video_file: videoFile.path,
        platforms: selectedPlatforms,
        metadata,
        scheduled_time: isScheduled ? `${format(scheduleDate, 'yyyy-MM-dd')}T${scheduleTime}:00` : null
      };

      const endpoint = isScheduled ? '/api/publish/schedule' : '/api/publish/multi';
      const response = await axios.post(
        `${API_URL}${endpoint}`,
        publishData,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast.success(isScheduled ? 'Video scheduled successfully!' : 'Video published successfully!');
      onClose();
    } catch (error) {
      console.error('Error publishing:', error);
      toast.error(error.response?.data?.detail || 'Failed to publish video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-slate-800 max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="publish-modal">
        <DialogHeader>
          <DialogTitle className="text-white">Publish Video</DialogTitle>
          <DialogDescription className="text-slate-400">
            Choose platforms and customize your video details
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Platform Selection */}
          <div className="space-y-3">
            <Label className="text-slate-300">Select Platforms</Label>
            <div className="grid grid-cols-3 gap-3">
              {platforms.map(platform => {
                const PlatformIcon = platform.icon;
                const isConnected = isPlatformConnected(platform.id);
                const isSelected = selectedPlatforms.includes(platform.id);

                return (
                  <div key={platform.id}>
                    <button
                      onClick={() => isConnected && togglePlatform(platform.id)}
                      disabled={!isConnected}
                      className={`w-full p-4 rounded-lg border-2 transition-all ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-500/10'
                          : isConnected
                          ? 'border-slate-700 hover:border-slate-600'
                          : 'border-slate-800 opacity-50 cursor-not-allowed'
                      }`}
                      data-testid={`platform-${platform.id}`}
                    >
                      <div className={`p-2 rounded-lg ${platform.bgColor} mx-auto w-fit`}>
                        <PlatformIcon className={`w-6 h-6 ${platform.color}`} />
                      </div>
                      <p className="text-white text-sm mt-2">{platform.name}</p>
                      {!isConnected && (
                        <p className="text-xs text-red-400 mt-1">Not connected</p>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>

            {selectedPlatforms.some(p => !isPlatformConnected(p)) && (
              <Alert className="bg-yellow-500/10 border-yellow-500/50">
                <AlertCircle className="h-4 w-4 text-yellow-500" />
                <AlertDescription className="text-yellow-200">
                  Some selected platforms are not connected. Please configure credentials or connect accounts first.
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Metadata */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-slate-300">Title</Label>
              <Input
                value={metadata.title}
                onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white"
                placeholder="Video title"
                data-testid="publish-title"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Description</Label>
              <Textarea
                value={metadata.description}
                onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white min-h-[100px]"
                placeholder="Video description"
                data-testid="publish-description"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Hashtags</Label>
              <Input
                value={metadata.hashtags}
                onChange={(e) => setMetadata({ ...metadata, hashtags: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white"
                placeholder="#motivation #success #viral"
                data-testid="publish-hashtags"
              />
            </div>
          </div>

          {/* Scheduling */}
          <div className="space-y-3">
            <Label className="text-slate-300">Schedule (Optional)</Label>
            <div className="grid grid-cols-2 gap-3">
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
                    data-testid="schedule-date-picker"
                  >
                    <CalendarIcon className="w-4 h-4 mr-2" />
                    {scheduleDate ? format(scheduleDate, 'PPP') : 'Pick date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-slate-800 border-slate-700">
                  <Calendar
                    mode="single"
                    selected={scheduleDate}
                    onSelect={setScheduleDate}
                    className="rounded-md"
                  />
                </PopoverContent>
              </Popover>

              <Input
                type="time"
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white"
                data-testid="schedule-time-input"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1 bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
              disabled={loading}
            >
              Cancel
            </Button>
            {scheduleDate && scheduleTime && (
              <Button
                onClick={() => handlePublish(true)}
                disabled={loading || selectedPlatforms.length === 0}
                className="flex-1 bg-orange-600 hover:bg-orange-700"
                data-testid="schedule-publish-button"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <CalendarIcon className="w-4 h-4 mr-2" />
                )}
                Schedule
              </Button>
            )}
            <Button
              onClick={() => handlePublish(false)}
              disabled={loading || selectedPlatforms.length === 0}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              data-testid="instant-publish-button"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Upload className="w-4 h-4 mr-2" />
              )}
              Publish Now
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PublishModal;