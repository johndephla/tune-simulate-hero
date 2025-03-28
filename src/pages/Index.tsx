
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { HelpCircleIcon, SettingsIcon } from "lucide-react";
import SongHistory from "@/components/SongHistory";
import ConnectionStatus from "@/components/ConnectionStatus";
import GenerateForm, { SongResult } from "@/components/GenerateForm";
import HelpDialog from "@/components/HelpDialog";
import SettingsDialog from "@/components/SettingsDialog";

const Index = () => {
  const [history, setHistory] = useState<SongResult[]>([]);
  const [helpOpen, setHelpOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Status query to check if server is running and bot is logged in
  const statusQuery = useQuery({
    queryKey: ["status"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/status");
      if (!response.ok) {
        throw new Error("API server not running");
      }
      return response.json();
    },
    refetchInterval: 5000 // Check status every 5 seconds
  });

  // Determine if server is connected based on the status query
  const isServerConnected = !statusQuery.isError && statusQuery.data?.connected;

  const handleSongGenerated = (result: SongResult) => {
    setHistory(prev => [result, ...prev].slice(0, 10)); // Keep only the 10 most recent songs
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">Suno AI Automation</h1>
        <p className="text-gray-600 mb-4">Generate AI music using Suno.ai with automated browser interaction</p>
        
        {/* Connection Status Indicator - Prominent at the top */}
        <div className="flex justify-center mb-6">
          <ConnectionStatus />
        </div>
        
        <div className="flex justify-center gap-2 mt-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setHelpOpen(true)}
          >
            <HelpCircleIcon className="h-4 w-4 mr-1" />
            Help
          </Button>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setSettingsOpen(true)}
          >
            <SettingsIcon className="h-4 w-4 mr-1" />
            Settings
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 md:col-span-2 shadow-md">
          <GenerateForm 
            isServerConnected={isServerConnected} 
            onGenerate={handleSongGenerated} 
          />
        </Card>
        
        <Card className="p-6 shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Song History</h2>
          <SongHistory history={history} />
        </Card>
      </div>

      {/* Help Dialog */}
      <HelpDialog open={helpOpen} onOpenChange={setHelpOpen} />

      {/* Settings Dialog */}
      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
};

export default Index;
