import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Loader2, Image as ImageIcon, RefreshCw, Check } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VisualSelector = ({ script, onVisualsSelected, existingVisuals }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [visualPrompt, setVisualPrompt] = useState('');
  const [generatedVisuals, setGeneratedVisuals] = useState(existingVisuals || []);
  const [selectedVisuals, setSelectedVisuals] = useState(existingVisuals || []);

  const handleGenerateVisuals = async () => {
    if (!script) {
      toast.error('No script available');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/api/content/generate-visuals`,
        {
          script: script.story || script.hook,
          niche: script.niche || 'general',
          style: visualPrompt || 'modern',
          count: 5
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setGeneratedVisuals(response.data.visuals || []);
      toast.success('Visuals generated successfully!');
    } catch (error) {
      console.error('Error generating visuals:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate visuals');
    } finally {
      setLoading(false);
    }
  };

  const toggleVisualSelection = (visual) => {
    if (selectedVisuals.find(v => v.url === visual.url)) {
      setSelectedVisuals(selectedVisuals.filter(v => v.url !== visual.url));
    } else {
      setSelectedVisuals([...selectedVisuals, visual]);
    }
  };

  const isSelected = (visual) => {
    return selectedVisuals.find(v => v.url === visual.url);
  };

  return (
    <div className="space-y-6" data-testid="visual-selector">
      <Card className="p-6 bg-slate-800/30 border-slate-700">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label className="text-slate-300">Visual Style (Optional)</Label>
            <Input
              value={visualPrompt}
              onChange={(e) => setVisualPrompt(e.target.value)}
              placeholder="e.g., modern, minimalist, vibrant, dark"
              className="bg-slate-800 border-slate-700 text-white"
              data-testid="visual-prompt-input"
            />
          </div>

          <Button
            onClick={handleGenerateVisuals}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700"
            data-testid="generate-visuals-button"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Visuals...
              </>
            ) : (
              <>
                <ImageIcon className="w-4 h-4 mr-2" />
                Generate AI Visuals
              </>
            )}
          </Button>
        </div>
      </Card>

      {generatedVisuals.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-slate-300">Select visuals for your video (click to select)</p>
            <p className="text-sm text-slate-400">{selectedVisuals.length} selected</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {generatedVisuals.map((visual, index) => (
              <div
                key={index}
                onClick={() => toggleVisualSelection(visual)}
                className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                  isSelected(visual) 
                    ? 'border-indigo-500 ring-2 ring-indigo-500/50' 
                    : 'border-slate-700 hover:border-slate-600'
                }`}
                data-testid={`visual-item-${index}`}
              >
                <img
                  src={visual.url}
                  alt={`Visual ${index + 1}`}
                  className="w-full h-48 object-cover"
                />
                {isSelected(visual) && (
                  <div className="absolute top-2 right-2 bg-indigo-600 rounded-full p-1">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleGenerateVisuals}
              disabled={loading}
              className="flex-1 bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Regenerate
            </Button>
            <Button
              onClick={() => onVisualsSelected(selectedVisuals)}
              disabled={selectedVisuals.length === 0}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              data-testid="proceed-to-preview-button"
            >
              Proceed to Preview →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualSelector;