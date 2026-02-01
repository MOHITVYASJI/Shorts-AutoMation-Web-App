import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, Mic, Image, Video, Upload } from 'lucide-react';
import ScriptGenerator from '@/components/create/ScriptGenerator';
import VoiceSelector from '@/components/create/VoiceSelector';
import VisualSelector from '@/components/create/VisualSelector';
import VideoPreview from '@/components/create/VideoPreview';
import PublishModal from '@/components/create/PublishModal';

const CreateVideo = () => {
  const [activeTab, setActiveTab] = useState('script');
  const [generatedScript, setGeneratedScript] = useState(null);
  const [generatedVoice, setGeneratedVoice] = useState(null);
  const [selectedVisuals, setSelectedVisuals] = useState([]);
  const [renderJobId, setRenderJobId] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [showPublishModal, setShowPublishModal] = useState(false);

  const handleScriptGenerated = (script) => {
    setGeneratedScript(script);
    setActiveTab('voice');
  };

  const handleVoiceGenerated = (voice) => {
    setGeneratedVoice(voice);
    setActiveTab('visuals');
  };

  const handleVisualsSelected = (visuals) => {
    setSelectedVisuals(visuals);
    setActiveTab('preview');
  };

  const handleVideoRendered = (jobId, file) => {
    setRenderJobId(jobId);
    setVideoFile(file);
  };

  const canProceedToVoice = generatedScript !== null;
  const canProceedToVisuals = generatedVoice !== null;
  const canProceedToPreview = selectedVisuals.length > 0;

  return (
    <div className="space-y-6" data-testid="create-video-page">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Create Video</h1>
        <p className="text-slate-400">Generate AI-powered short videos in minutes</p>
      </div>

      <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Video Creation Workflow</CardTitle>
          <CardDescription className="text-slate-400">
            Follow the steps below to create your short video
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4 bg-slate-800">
              <TabsTrigger value="script" className="data-[state=active]:bg-indigo-600" data-testid="tab-script">
                <Sparkles className="w-4 h-4 mr-2" />
                Script
              </TabsTrigger>
              <TabsTrigger 
                value="voice" 
                disabled={!canProceedToVoice}
                className="data-[state=active]:bg-indigo-600"
                data-testid="tab-voice"
              >
                <Mic className="w-4 h-4 mr-2" />
                Voice
              </TabsTrigger>
              <TabsTrigger 
                value="visuals" 
                disabled={!canProceedToVisuals}
                className="data-[state=active]:bg-indigo-600"
                data-testid="tab-visuals"
              >
                <Image className="w-4 h-4 mr-2" />
                Visuals
              </TabsTrigger>
              <TabsTrigger 
                value="preview" 
                disabled={!canProceedToPreview}
                className="data-[state=active]:bg-indigo-600"
                data-testid="tab-preview"
              >
                <Video className="w-4 h-4 mr-2" />
                Preview
              </TabsTrigger>
            </TabsList>

            <TabsContent value="script" className="mt-6">
              <ScriptGenerator 
                onScriptGenerated={handleScriptGenerated}
                existingScript={generatedScript}
              />
            </TabsContent>

            <TabsContent value="voice" className="mt-6">
              <VoiceSelector 
                script={generatedScript}
                onVoiceGenerated={handleVoiceGenerated}
                existingVoice={generatedVoice}
              />
            </TabsContent>

            <TabsContent value="visuals" className="mt-6">
              <VisualSelector 
                script={generatedScript}
                onVisualsSelected={handleVisualsSelected}
                existingVisuals={selectedVisuals}
              />
            </TabsContent>

            <TabsContent value="preview" className="mt-6">
              <VideoPreview 
                script={generatedScript}
                voice={generatedVoice}
                visuals={selectedVisuals}
                onVideoRendered={handleVideoRendered}
                onPublish={() => setShowPublishModal(true)}
                videoFile={videoFile}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {showPublishModal && videoFile && (
        <PublishModal
          open={showPublishModal}
          onClose={() => setShowPublishModal(false)}
          videoFile={videoFile}
          scriptData={generatedScript}
        />
      )}
    </div>
  );
};

export default CreateVideo;