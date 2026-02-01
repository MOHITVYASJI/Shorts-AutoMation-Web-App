import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Loader2, Image as ImageIcon, RefreshCw, Check } from 'lucide-react';
import { toast } from 'sonner';
import { contentAPI } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VisualSelector = ({ script, onVisualsSelected, existingVisuals }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [visualStyle, setVisualStyle] = useState('realistic');
  const [generatedVisuals, setGeneratedVisuals] = useState(existingVisuals || []);
  const [selectedVisuals, setSelectedVisuals] = useState(existingVisuals || []);

  const handleGenerateVisuals = async () => {
    if (!script) {
      toast.error('No script available');
      return;
    }

    setLoading(true);
    try {
      const response = await contentAPI.generateVisuals({
        script: script,
        niche: script.niche || 'general',
        style: visualStyle || 'realistic',
        count: 3
      });

      // Backend returns { success: true, image_paths: [...], count: 3 }
      const imagePaths = response.image_paths || [];
      
      // Convert paths to full URLs
      const visualsWithUrls = imagePaths.map((path, index) => ({
        url: path.startsWith('http') ? path : `${API_URL}${path}`,
        path: path,
        index: index
      }));

      setGeneratedVisuals(visualsWithUrls);
      setSelectedVisuals(visualsWithUrls); // Auto-select all generated visuals
      toast.success(`Generated ${visualsWithUrls.length} visuals successfully!`);
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
            <Label className="text-slate-300">Visual Style</Label>
            <select
              value={visualStyle}
              onChange={(e) => setVisualStyle(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-white rounded-md"
              data-testid="visual-style-select"
            >
              <option value="realistic">Realistic / Photorealistic</option>
              <option value="animated">Animated / Illustrated</option>
              <option value="minimalist">Minimalist / Modern</option>
              <option value="cinematic">Cinematic / Dramatic</option>
            </select>
          </div>

          <div className="p-4 bg-slate-800 rounded-lg">
            <p className="text-sm text-slate-400 mb-2">Script Context:</p>
            <p className="text-white text-sm line-clamp-2">
              {script?.title || script?.hook}
            </p>
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
            <p className="text-slate-300">Select visuals for your video (click to toggle)</p>
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
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23334155"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" fill="%23cbd5e1" font-family="sans-serif" font-size="14"%3EImage%3C/text%3E%3C/svg%3E';
                  }}
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
              Proceed to Preview ({selectedVisuals.length}) →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualSelector;