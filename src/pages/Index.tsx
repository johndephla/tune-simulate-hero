
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import { Loader2, MusicIcon, DownloadIcon, LinkIcon } from "lucide-react";
import SongHistory from "@/components/SongHistory";
import { useForm } from "react-hook-form";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form";

interface GenerateFormData {
  prompt: string;
  download: boolean;
}

interface SongResult {
  success: boolean;
  url: string;
  prompt: string;
  file_path?: string;
  download_error?: string;
}

const Index = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [songResult, setSongResult] = useState<SongResult | null>(null);
  const [history, setHistory] = useState<SongResult[]>([]);

  const form = useForm<GenerateFormData>({
    defaultValues: {
      prompt: "",
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
    refetchInterval: 30000 // Check status every 30 seconds
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
        <p className="text-gray-600">Generate AI music using Suno.ai with automated browser interaction</p>
        
        {/* Status indicator */}
        <div className="mt-4 flex items-center justify-center gap-2">
          <div className={`h-3 w-3 rounded-full ${statusQuery.isLoading ? 'bg-yellow-500' : statusQuery.isError ? 'bg-red-500' : 'bg-green-500'}`}></div>
          <span className="text-sm">
            {statusQuery.isLoading ? 'Checking server status...' : 
             statusQuery.isError ? 'Server offline' : 
             `Server online${statusQuery.data?.logged_in ? ', logged in' : ', not logged in'}`}
          </span>
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
                    <FormLabel>Song Prompt</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Enter a description for your song (e.g. 'A happy techno song about robots')" 
                        className="min-h-[100px]" 
                        disabled={isGenerating}
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
                      Download the song automatically
                    </FormLabel>
                  </FormItem>
                )}
              />
              
              <Button 
                type="submit" 
                disabled={isGenerating || statusQuery.isError} 
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
    </div>
  );
};

export default Index;
