import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { contentAPI } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const ScriptGenerator = ({ onScriptGenerated, existingScript }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [niches, setNiches] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [durations, setDurations] = useState([]);
  
  const [formData, setFormData] = useState({
    platform: 'youtube',
    niche: '',
    language: 'English',
    duration: 30
  });

  const [generatedScript, setGeneratedScript] = useState(existingScript || null);

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      const [nichesRes, langsRes, dursRes] = await Promise.all([
        contentAPI.getNiches(),
        contentAPI.getLanguages(),
        contentAPI.getDurations()
      ]);
      setNiches(nichesRes.niches || []);
      setLanguages(langsRes.languages || []);
      setDurations(dursRes.durations || []);
    } catch (error) {
      console.error('Error fetching options:', error);
      toast.error('Failed to load options');
    }
  };

  const handleGenerate = async () => {
    if (!formData.niche) {
      toast.error('Please select a niche');
      return;
    }

    setLoading(true);
    try {
      const response = await contentAPI.generateScript(formData);
      const scriptData = response.script || response;
      setGeneratedScript(scriptData);
      toast.success('Script generated successfully!');
      onScriptGenerated(scriptData);
    } catch (error) {
      console.error('Error generating script:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate script');
    } finally {
      setLoading(false);
    }
  };

  const handleEditScript = (field, value) => {
    setGeneratedScript({
      ...generatedScript,
      [field]: value
    });
    onScriptGenerated({
      ...generatedScript,
      [field]: value
    });
  };

  return (
    <div className="space-y-6" data-testid="script-generator">
      {!generatedScript ? (
        <Card className="p-6 bg-slate-800/30 border-slate-700">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Platform</Label>
                <Select value={formData.platform} onValueChange={(value) => setFormData({ ...formData, platform: value })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="platform-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="youtube">YouTube Shorts</SelectItem>
                    <SelectItem value="instagram">Instagram Reels</SelectItem>
                    <SelectItem value="facebook">Facebook Reels</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Niche *</Label>
                <Select value={formData.niche} onValueChange={(value) => setFormData({ ...formData, niche: value })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="niche-select">
                    <SelectValue placeholder="Select a niche" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {niches.map(niche => (
                      <SelectItem key={niche} value={niche}>
                        {niche.replace('_', ' ').charAt(0).toUpperCase() + niche.replace('_', ' ').slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Language</Label>
                <Select value={formData.language} onValueChange={(value) => setFormData({ ...formData, language: value })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="language-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {languages.map(lang => (
                      <SelectItem key={typeof lang === 'string' ? lang : lang.code} value={typeof lang === 'string' ? lang : lang.name}>
                        {typeof lang === 'string' ? lang.charAt(0).toUpperCase() + lang.slice(1) : lang.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Duration (seconds)</Label>
                <Select value={formData.duration.toString()} onValueChange={(value) => setFormData({ ...formData, duration: parseInt(value) })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white" data-testid="duration-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {durations.map(dur => {
                      const val = typeof dur === 'number' ? dur : dur.value;
                      return (
                        <SelectItem key={val} value={val.toString()}>
                          {val} seconds
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
              data-testid="generate-script-button"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating Script...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate AI Script
                </>
              )}
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card className="p-6 bg-slate-800/30 border-slate-700">
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300">Title</Label>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleGenerate}
                    disabled={loading}
                    className="text-indigo-400 hover:text-indigo-300"
                  >
                    <RefreshCw className="w-4 h-4 mr-1" />
                    Regenerate
                  </Button>
                </div>
                <Textarea
                  value={generatedScript.title || ''}
                  onChange={(e) => handleEditScript('title', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white min-h-[60px]"
                  data-testid="script-title"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Hook (0-2 seconds)</Label>
                <Textarea
                  value={generatedScript.hook || ''}
                  onChange={(e) => handleEditScript('hook', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white min-h-[80px]"
                  data-testid="script-hook"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Story / Main Content</Label>
                <Textarea
                  value={generatedScript.body || generatedScript.story || ''}
                  onChange={(e) => handleEditScript('body', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white min-h-[120px]"
                  data-testid="script-body"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Ending / CTA</Label>
                <Textarea
                  value={generatedScript.ending || ''}
                  onChange={(e) => handleEditScript('ending', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white min-h-[80px]"
                  data-testid="script-ending"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Description</Label>
                <Textarea
                  value={generatedScript.description || ''}
                  onChange={(e) => handleEditScript('description', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white min-h-[80px]"
                  data-testid="script-description"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Hashtags</Label>
                <Textarea
                  value={Array.isArray(generatedScript.hashtags) ? generatedScript.hashtags.join(' ') : (generatedScript.hashtags || '')}
                  onChange={(e) => handleEditScript('hashtags', e.target.value.split(' ').filter(h => h))}
                  className="bg-slate-800 border-slate-700 text-white min-h-[60px]"
                  placeholder="#motivation #success #viral"
                  data-testid="script-hashtags"
                />
              </div>
            </div>
          </Card>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setGeneratedScript(null)}
              className="flex-1 bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
            >
              Start Over
            </Button>
            <Button
              onClick={() => onScriptGenerated(generatedScript)}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              data-testid="proceed-to-voice-button"
            >
              Proceed to Voice →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScriptGenerator;