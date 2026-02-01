import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Loader2, Mic, Play, Pause } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VoiceSelector = ({ script, onVoiceGenerated, existingVoice }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('default');
  const [generatedVoice, setGeneratedVoice] = useState(existingVoice || null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState(null);

  useEffect(() => {
    fetchVoices();
    return () => {
      if (audio) {
        audio.pause();
      }
    };
  }, []);

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/content/voices`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVoices(response.data.voices || []);
    } catch (error) {
      console.error('Error fetching voices:', error);
      // Set default voices if API fails
      setVoices([
        { id: 'default', name: 'Default Voice', language: 'english' },
        { id: 'male1', name: 'Male Voice 1', language: 'english' },
        { id: 'female1', name: 'Female Voice 1', language: 'english' }
      ]);
    }
  };

  const handleGenerateVoice = async () => {
    if (!script) {
      toast.error('No script available');
      return;
    }

    setLoading(true);
    try {
      const fullScript = `${script.hook} ${script.story} ${script.ending}`;
      const response = await axios.post(
        `${API_URL}/api/content/generate-voice`,
        {
          text: fullScript,
          voice_id: selectedVoice,
          language: script.language || 'english'
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setGeneratedVoice(response.data);
      toast.success('Voice generated successfully!');
      onVoiceGenerated(response.data);
    } catch (error) {
      console.error('Error generating voice:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate voice');
    } finally {
      setLoading(false);
    }
  };

  const togglePlayAudio = () => {
    if (!generatedVoice?.audio_url) return;

    if (audio && !audio.paused) {
      audio.pause();
      setIsPlaying(false);
    } else {
      const newAudio = new Audio(generatedVoice.audio_url);
      newAudio.play();
      newAudio.onended = () => setIsPlaying(false);
      setAudio(newAudio);
      setIsPlaying(true);
    }
  };

  return (
    <div className="space-y-6" data-testid="voice-selector">
      {!generatedVoice ? (
        <Card className="p-6 bg-slate-800/30 border-slate-700">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-slate-300">Select Voice</Label>
              <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="voice-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  {voices.map(voice => (
                    <SelectItem key={voice.id} value={voice.id}>
                      {voice.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="p-4 bg-slate-800 rounded-lg">
              <p className="text-sm text-slate-400 mb-2">Script Preview:</p>
              <p className="text-white text-sm">
                {script?.hook} {script?.story?.substring(0, 100)}...
              </p>
            </div>

            <Button
              onClick={handleGenerateVoice}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
              data-testid="generate-voice-button"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating Voice...
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4 mr-2" />
                  Generate Voice
                </>
              )}
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card className="p-6 bg-slate-800/30 border-slate-700">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-medium">Voice Generated</h3>
                  <p className="text-sm text-slate-400">Duration: {generatedVoice.duration}s</p>
                </div>
                <Button
                  onClick={togglePlayAudio}
                  className="bg-indigo-600 hover:bg-indigo-700"
                  data-testid="play-voice-button"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Play
                    </>
                  )}
                </Button>
              </div>

              <div className="p-4 bg-slate-800 rounded-lg">
                <p className="text-sm text-slate-400">Voice ID: {generatedVoice.voice_id}</p>
                <p className="text-sm text-slate-400">File: {generatedVoice.filename}</p>
              </div>
            </div>
          </Card>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setGeneratedVoice(null)}
              className="flex-1 bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
            >
              Regenerate
            </Button>
            <Button
              onClick={() => onVoiceGenerated(generatedVoice)}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              data-testid="proceed-to-visuals-button"
            >
              Proceed to Visuals →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceSelector;