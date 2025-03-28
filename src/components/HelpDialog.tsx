
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
          <DialogTitle>Suno.ai Automation with Selenium</DialogTitle>
          <DialogDescription>
            <div className="mt-4 space-y-3">
              <div>
                <h4 className="font-medium">Getting Started</h4>
                <p className="text-sm">This app uses Selenium to automate the Suno.ai website for song generation. Make sure to have ChromeDriver and Selenium running.</p>
              </div>
              
              <div>
                <h4 className="font-medium">How It Works</h4>
                <p className="text-sm">Enter a prompt, style, and title for your song. The system will use Selenium to login to Suno.ai and generate the song for you automatically.</p>
              </div>
              
              <div>
                <h4 className="font-medium">Configuration</h4>
                <ul className="text-sm list-disc pl-5">
                  <li>Make sure Python and the required packages are installed</li>
                  <li>Run the included `main.py` script to start the Selenium service</li>
                  <li>Configure your Suno.ai login credentials in the .env file</li>
                  <li>The connection status indicator shows if Selenium is currently available</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium">Troubleshooting</h4>
                <ul className="text-sm list-disc pl-5">
                  <li>If connection fails, make sure the Python service is running</li>
                  <li>Check the credentials in your .env file are correct</li>
                  <li>Review the console or logs for any Selenium errors</li>
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
