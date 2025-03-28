import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import { Loader2, MusicIcon, DownloadIcon, LinkIcon, SettingsIcon, HelpCircleIcon, InfoIcon } from "lucide-react";
import SongHistory from "@/components/SongHistory";
import { useForm } from "react-hook-form";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form";
import ConnectionStatus from "@/components/ConnectionStatus";

interface GenerateFormData {
  prompt: string;
  style: string;
  title: string;
  instrumental: boolean;
  download: boolean;
}

interface SongResult {
  success: boolean;
  url: string;
  prompt: string;
  style?: string;
  title?: string;
  file_path?: string;
  download_error?: string;
}

const Index = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [songResult, setSongResult] = useState<SongResult | null>(null);
  const [history, setHistory] = useState<SongResult[]>([]);
  const [helpOpen, setHelpOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const form = useForm<GenerateFormData>({
    defaultValues: {
      prompt: "",
      style: "",
      title: "",
      instrumental: true,
      download: true
    }
  });

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

  const onSubmit = async (data: GenerateFormData) => {
    if (!data.prompt.trim()) {
      toast.error("Please enter a prompt");
      return;
    }

    setIsGenerating(true);
    setSongResult(null);

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: data.prompt,
          style: data.style || undefined,
          title: data.title || undefined,
          instrumental: data.instrumental,
          download: data.download
        }),
      });

      const result = await response.json();
      setSongResult(result);
      
      if (result.success) {
        toast.success("Song generated successfully!");
        setHistory(prev => [result, ...prev].slice(0, 10)); // Keep only the 10 most recent songs
        form.reset();
      } else {
        toast.error(`Generation failed: ${result.error}`);
      }
    } catch (error) {
      toast.error("Failed to connect to the server. Is the bot running?");
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
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
          <h2 className="text-2xl font-semibold mb-4">Generate Song</h2>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Song Prompt (Lyrics)</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Enter a description for your song (e.g. 'A happy techno song about robots')" 
                        className="min-h-[100px]" 
                        disabled={isGenerating}
                        maxLength={500}
                        showCount={true}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Be descriptive about the mood, style, and theme of your song
                    </FormDescription>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="style"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Style of Music</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Enter style of music (e.g. 'Electronic, dance, techno')" 
                        className="min-h-[60px]" 
                        disabled={isGenerating}
                        maxLength={200}
                        showCount={true}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Specify the genre or musical style for your song
                    </FormDescription>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Song Title</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter a title for your song" 
                        disabled={isGenerating}
                        maxLength={80}
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              
              <div className="flex flex-col sm:flex-row sm:justify-between gap-4">
                <FormField
                  control={form.control}
                  name="instrumental"
                  render={({ field }) => (
                    <FormItem className="flex items-center gap-2">
                      <FormControl>
                        <input 
                          type="checkbox" 
                          checked={field.value}
                          onChange={field.onChange}
                          disabled={isGenerating}
                          id="instrumental-checkbox"
                          className="h-4 w-4"
                        />
                      </FormControl>
                      <FormLabel htmlFor="instrumental-checkbox" className="cursor-pointer m-0">
                        Instrumental mode (no vocals)
                      </FormLabel>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="download"
                  render={({ field }) => (
                    <FormItem className="flex items-center gap-2">
                      <FormControl>
                        <input 
                          type="checkbox" 
                          checked={field.value}
                          onChange={field.onChange}
                          disabled={isGenerating}
                          id="download-checkbox"
                          className="h-4 w-4"
                        />
                      </FormControl>
                      <FormLabel htmlFor="download-checkbox" className="cursor-pointer m-0">
                        Download song automatically
                      </FormLabel>
                    </FormItem>
                  )}
                />
              </div>
              
              <Button 
                type="submit" 
                disabled={isGenerating || statusQuery.isError || (statusQuery.data && !statusQuery.data.connected)} 
                className="w-full"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Song...
                  </>
                ) : (
                  <>
                    <MusicIcon className="mr-2 h-4 w-4" />
                    Generate Song
                  </>
                )}
              </Button>
            </form>
          </Form>

          {songResult && songResult.success && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <h3 className="font-medium text-green-800 mb-2">Song Created!</h3>
              <p className="text-sm mb-3">"{songResult.prompt}"</p>
              
              <div className="flex flex-col sm:flex-row gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => window.open(songResult.url, '_blank')}
                  className="flex-1"
                >
                  <LinkIcon className="mr-2 h-4 w-4" />
                  Open in Browser
                </Button>
                
                {songResult.file_path && (
                  <Button 
                    variant="secondary" 
                    onClick={() => window.open(`file://${songResult.file_path}`, '_blank')}
                    className="flex-1"
                  >
                    <DownloadIcon className="mr-2 h-4 w-4" />
                    Open Downloaded File
                  </Button>
                )}
              </div>
              
              {songResult.download_error && (
                <p className="text-sm text-red-500 mt-2">Download failed: {songResult.download_error}</p>
              )}
            </div>
          )}
        </Card>
        
        <Card className="p-6 shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Song History</h2>
          <SongHistory history={history} />
        </Card>
      </div>

      {/* Help Dialog */}
      <Dialog open={helpOpen} onOpenChange={setHelpOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>How to Use Suno AI Automation</DialogTitle>
            <DialogDescription>
              <div className="mt-4 space-y-3">
                <div>
                  <h4 className="font-medium">Getting Started</h4>
                  <p className="text-sm">Ensure the automation server is running in the background. Wait for the status indicator to show "Server online, logged in".</p>
                </div>
                
                <div>
                  <h4 className="font-medium">Creating Songs</h4>
                  <p className="text-sm">Enter a descriptive prompt for your song. Be specific about genre, mood, instruments, and themes. Click "Generate Song" and wait for the process to complete.</p>
                </div>
                
                <div>
                  <h4 className="font-medium">Tips for Better Results</h4>
                  <ul className="text-sm list-disc pl-5">
                    <li>Include a music genre (pop, rock, jazz, etc.)</li>
                    <li>Describe the mood or emotion (happy, melancholic, energetic)</li>
                    <li>Mention specific instruments if desired</li>
                    <li>Keep prompts concise but descriptive</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium">Troubleshooting</h4>
                  <ul className="text-sm list-disc pl-5">
                    <li>If the server shows "offline", restart the Python application</li>
                    <li>If login fails, check your Chrome profile settings</li>
                    <li>For other issues, check the log file</li>
                  </ul>
                </div>
              </div>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Settings</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <Label htmlFor="chrome-path">Chrome Profile Path</Label>
              <Input 
                id="chrome-path" 
                placeholder="C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
                disabled
                className="text-sm text-muted-foreground"
              />
              <p className="text-xs text-muted-foreground">To change this setting, edit the .env file</p>
            </div>
            
            <div className="space-y-1">
              <Label htmlFor="headless-mode">Headless Mode</Label>
              <div className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  id="headless-mode"
                  className="h-4 w-4"
                  disabled
                />
                <span className="text-sm text-muted-foreground">Edit .env file to change</span>
              </div>
              <p className="text-xs text-muted-foreground">When enabled, the browser runs in the background</p>
            </div>

            <div className="bg-blue-50 p-3 rounded-md mt-4">
              <div className="flex items-start gap-2">
                <InfoIcon className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-blue-700">Settings can only be changed by editing the .env file in the application directory.</p>
                  <p className="text-xs text-blue-600 mt-1">After changing settings, restart the application.</p>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Index;
