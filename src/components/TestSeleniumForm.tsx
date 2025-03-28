
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Loader2, Globe, PlayCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form";

export interface TestFormData {
  url: string;
  action: string;
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

interface TestSeleniumFormProps {
  onTestComplete: (result: SongResult) => void;
}

const TestSeleniumForm = ({ onTestComplete }: TestSeleniumFormProps) => {
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<SongResult | null>(null);

  const form = useForm<TestFormData>({
    defaultValues: {
      url: "https://www.google.com",
      action: "Navigate to the URL and take a screenshot"
    }
  });

  const onSubmit = async (data: TestFormData) => {
    if (!data.url.trim()) {
      toast.error("Please enter a URL");
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      // Simulate a Selenium test
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // This is just a simulation - in a real app we would call the Selenium service
      const isSuccess = Math.random() > 0.3;
      
      const result = {
        success: isSuccess,
        url: data.url,
        prompt: data.action,
        style: "Selenium Test",
        title: "Automation Test",
        file_path: isSuccess ? "/path/to/screenshot.png" : undefined,
        download_error: isSuccess ? undefined : "Failed to connect to Selenium"
      };
      
      setTestResult(result);
      
      if (result.success) {
        toast.success("Selenium test completed successfully!");
        onTestComplete(result);
      } else {
        toast.error(`Test failed: ${result.download_error}`);
      }
    } catch (error) {
      toast.error("Failed to run Selenium test. Is Selenium running?");
      console.error(error);
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <>
      <h2 className="text-2xl font-semibold mb-4">Test Selenium</h2>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="url"
            render={({ field }) => (
              <FormItem>
                <FormLabel>URL to Visit</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="https://www.example.com" 
                    disabled={isTesting}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Enter the URL you want Selenium to navigate to
                </FormDescription>
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="action"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Action to Perform</FormLabel>
                <FormControl>
                  <Textarea 
                    placeholder="Describe what action to perform (e.g., 'Click login button')" 
                    className="min-h-[100px]" 
                    disabled={isTesting}
                    maxLength={500}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Describe the action you want Selenium to perform
                </FormDescription>
              </FormItem>
            )}
          />
          
          <Button 
            type="submit" 
            disabled={isTesting} 
            className="w-full"
          >
            {isTesting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing Selenium...
              </>
            ) : (
              <>
                <PlayCircle className="mr-2 h-4 w-4" />
                Run Selenium Test
              </>
            )}
          </Button>
        </form>
      </Form>

      {testResult && (
        <div className={`mt-6 p-4 ${testResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border rounded-md`}>
          <h3 className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'} mb-2`}>
            {testResult.success ? 'Test Completed!' : 'Test Failed!'}
          </h3>
          <p className="text-sm mb-3">URL: {testResult.url}</p>
          <p className="text-sm mb-3">Action: "{testResult.prompt}"</p>
          
          {testResult.success ? (
            <Button 
              variant="outline" 
              onClick={() => window.open(testResult.url, '_blank')}
              className="w-full"
            >
              <Globe className="mr-2 h-4 w-4" />
              Open URL in Browser
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
