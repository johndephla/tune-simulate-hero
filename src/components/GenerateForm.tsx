
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Loader2, MusicIcon, DownloadIcon, LinkIcon } from "lucide-react";
import { useForm } from "react-hook-form";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form";

export interface GenerateFormData {
  prompt: string;
  style: string;
  title: string;
  instrumental: boolean;
  download: boolean;
}

export interface SongResult {
  success: boolean;
  url: string;
  prompt: string;
  style?: string;
  title?: string;
  file_path?: string;
  download_error?: string;
}

interface GenerateFormProps {
  isServerConnected: boolean;
  onGenerate: (song: SongResult) => void;
}

const GenerateForm = ({ isServerConnected, onGenerate }: GenerateFormProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [songResult, setSongResult] = useState<SongResult | null>(null);

  const form = useForm<GenerateFormData>({
    defaultValues: {
      prompt: "",
      style: "",
      title: "",
      instrumental: true,
      download: true
    }
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
        onGenerate(result);
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
    <>
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
            disabled={isGenerating || !isServerConnected} 
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
    </>
  );
};

export default GenerateForm;
