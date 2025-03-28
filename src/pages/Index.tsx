
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { HelpCircleIcon, SettingsIcon } from "lucide-react";
import SongHistory from "@/components/SongHistory";
import ConnectionStatus from "@/components/ConnectionStatus";
import TestSeleniumForm, { SongResult } from "@/components/TestSeleniumForm";
import HelpDialog from "@/components/HelpDialog";
import SettingsDialog from "@/components/SettingsDialog";

const Index = () => {
  const [history, setHistory] = useState<SongResult[]>([]);
  const [helpOpen, setHelpOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSongGenerated = (result: SongResult) => {
    setHistory(prev => [result, ...prev].slice(0, 10)); // Keep only the 10 most recent songs
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">Suno.ai Automation</h1>
        <p className="text-gray-600 mb-4">Automatically generate songs with Suno.ai through Selenium</p>
        
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
          <TestSeleniumForm 
            onTestComplete={handleSongGenerated} 
          />
        </Card>
        
        <Card className="p-6 shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Generated Songs</h2>
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
