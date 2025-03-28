
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Loader2, Music, PlayCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form";

export interface TestFormData {
  prompt: string;
  style: string;
  title: string;
  instrumental: boolean;
}

export interface SongResult {
  success: boolean;
  url?: string;
  prompt: string;
  style?: string;
  title?: string;
  file_path?: string;
  download_error?: string;
}

interface TestSeleniumFormProps {
  onTestComplete: (result: SongResult) => void;
}

const TestSeleniumForm = ({ onTestComplete }: TestSeleniumFormProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [testResult, setTestResult] = useState<SongResult | null>(null);
  const [simulateRequest, setSimulateRequest] = useState(false);

  const form = useForm<TestFormData>({
    defaultValues: {
      prompt: "A song about exploring space and discovering new worlds",
      style: "Epic orchestral soundtrack",
      title: "Cosmic Journey",
      instrumental: true
    }
  });

  const onSubmit = async (data: TestFormData) => {
    if (!data.prompt.trim()) {
      toast.error("Please enter a prompt for the song");
      return;
    }

    setIsGenerating(true);
    setTestResult(null);

    try {
      if (simulateRequest) {
        // Simulate a successful response after a delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const simulatedResult: SongResult = {
          success: true,
          url: "https://suno.example.com/song/123456",
          prompt: data.prompt,
          style: data.style,
          title: data.title,
          file_path: "/path/to/simulated/song.mp3"
        };
        
        setTestResult(simulatedResult);
        onTestComplete(simulatedResult);
        toast.success("Song generation simulated successfully!");
      } else {
        // Actual request to Selenium API
        const response = await fetch('http://localhost:8000/generate-song', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt: data.prompt,
            style: data.style,
            title: data.title,
            instrumental: data.instrumental
          }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to generate song");
        }
        
        const result = await response.json();
        
        setTestResult(result);
        
        if (result.success) {
          toast.success("Song generated successfully!");
          onTestComplete(result);
        } else {
          toast.error(`Generation failed: ${result.download_error}`);
        }
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Failed to generate song. Is Selenium running?");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <h2 className="text-2xl font-semibold mb-4">Generate Song with Suno.ai</h2>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="prompt"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Song Lyrics/Prompt</FormLabel>
                <FormControl>
                  <Textarea 
                    placeholder="Enter lyrics or a prompt for your song" 
                    className="min-h-[100px]" 
                    disabled={isGenerating}
                    maxLength={500}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Describe the lyrics or concept for your song
                </FormDescription>
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="style"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Music Style</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="e.g., Rock, Pop, Orchestral" 
                    disabled={isGenerating}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  The genre or style of music
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
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  A title for your generated song
                </FormDescription>
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="instrumental"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                <div className="space-y-0.5">
                  <FormLabel className="text-base">Instrumental Only</FormLabel>
                  <FormDescription>
                    Generate an instrumental version without vocals
                  </FormDescription>
                </div>
                <FormControl>
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={(e) => field.onChange(e.target.checked)}
                    className="h-4 w-4"
                  />
                </FormControl>
              </FormItem>
            )}
          />
          
          <div className="flex flex-row items-center justify-between rounded-lg border p-4 mb-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">Modalità Simulazione</FormLabel>
              <FormDescription>
                Simula le richieste senza un server Selenium
              </FormDescription>
            </div>
            <input
              type="checkbox"
              checked={simulateRequest}
              onChange={() => setSimulateRequest(!simulateRequest)}
              className="h-4 w-4"
            />
          </div>
          
          <Button 
            type="submit" 
            disabled={isGenerating} 
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Song...
              </>
            ) : (
              <>
                <Music className="mr-2 h-4 w-4" />
                {simulateRequest ? "Simulate Song Generation" : "Generate Song with Suno.ai"}
              </>
            )}
          </Button>
        </form>
      </Form>

      {testResult && (
        <div className={`mt-6 p-4 ${testResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border rounded-md`}>
          <h3 className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'} mb-2`}>
            {testResult.success ? 'Song Generated!' : 'Generation Failed!'}
          </h3>
          <p className="text-sm mb-1"><span className="font-medium">Title:</span> {testResult.title}</p>
          <p className="text-sm mb-1"><span className="font-medium">Style:</span> {testResult.style}</p>
          <p className="text-sm mb-3"><span className="font-medium">Prompt:</span> "{testResult.prompt}"</p>
          
          {testResult.success ? (
            <Button 
              variant="outline" 
              onClick={() => testResult.url && window.open(testResult.url, '_blank')}
              className="w-full"
            >
              <Music className="mr-2 h-4 w-4" />
              Listen to Your Song
            </Button>
          ) : (
            <p className="text-sm text-red-500 mt-2">Error: {testResult.download_error}</p>
          )}
        </div>
      )}
    </>
  );
};

export default TestSeleniumForm;
