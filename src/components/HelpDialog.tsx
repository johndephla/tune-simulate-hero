
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
          <DialogTitle>Selenium Automation Testing</DialogTitle>
          <DialogDescription>
            <div className="mt-4 space-y-3">
              <div>
                <h4 className="font-medium">Getting Started</h4>
                <p className="text-sm">This app is designed to test Selenium browser automation. Make sure to have ChromeDriver and Selenium installed.</p>
              </div>
              
              <div>
                <h4 className="font-medium">Testing Selenium</h4>
                <p className="text-sm">Enter a URL and action to test if Selenium can automate browser tasks. The status indicator shows if Selenium is currently connected.</p>
              </div>
              
              <div>
                <h4 className="font-medium">Configuration</h4>
                <ul className="text-sm list-disc pl-5">
                  <li>Make sure Chrome is installed</li>
                  <li>Install ChromeDriver that matches your Chrome version</li>
                  <li>Configure paths in the Settings dialog</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium">Troubleshooting</h4>
                <ul className="text-sm list-disc pl-5">
                  <li>If connection fails, check that ChromeDriver is running</li>
                  <li>Ensure your Chrome version matches ChromeDriver</li>
                  <li>Check system logs for Selenium errors</li>
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
