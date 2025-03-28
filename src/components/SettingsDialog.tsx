
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { InfoIcon } from "lucide-react";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SettingsDialog = ({ open, onOpenChange }: SettingsDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
  );
};

export default SettingsDialog;
