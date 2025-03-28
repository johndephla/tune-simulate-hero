
import React from 'react';
import { Button } from "@/components/ui/button";
import { LinkIcon, DownloadIcon } from "lucide-react";

interface SongResult {
  success: boolean;
  url: string;
  prompt: string;
  file_path?: string;
  download_error?: string;
}

interface SongHistoryProps {
  history: SongResult[];
}

const SongHistory: React.FC<SongHistoryProps> = ({ history }) => {
  if (history.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No songs generated yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
      {history.map((song, index) => (
        <div key={index} className="p-3 border rounded-md hover:bg-gray-50">
          <p className="text-sm font-medium mb-1 line-clamp-2">{song.prompt}</p>
          <div className="flex gap-2 mt-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => window.open(song.url, '_blank')}
              className="flex-1 h-8"
            >
              <LinkIcon className="h-3 w-3 mr-1" />
              <span className="text-xs">Open</span>
            </Button>
            
            {song.file_path && (
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={() => window.open(`file://${song.file_path}`, '_blank')}
                className="flex-1 h-8"
              >
                <DownloadIcon className="h-3 w-3 mr-1" />
                <span className="text-xs">File</span>
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SongHistory;
