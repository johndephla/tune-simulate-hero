
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";

interface HelpDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const HelpDialog = ({ open, onOpenChange }: HelpDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
  );
};

export default HelpDialog;
