
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Loader2, WifiOff, Wifi } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ConnectionStatusProps {
  className?: string;
}

const ConnectionStatus = ({ className }: ConnectionStatusProps) => {
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
  
  if (statusQuery.isLoading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
        <span className="text-sm">Checking connection...</span>
      </div>
    );
  }
  
  if (statusQuery.isError) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <WifiOff className="h-4 w-4 text-red-500" />
        <Badge variant="destructive">Server Offline</Badge>
      </div>
    );
  }
  
  const { connected, logged_in, error } = statusQuery.data;
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-2">
              {!connected ? (
                <>
                  <WifiOff className="h-4 w-4 text-red-500" />
                  <Badge variant="destructive">Disconnected</Badge>
                </>
              ) : !logged_in ? (
                <>
                  <Wifi className="h-4 w-4 text-yellow-500" />
                  <Badge variant="warning" className="bg-yellow-500">Connected, Not Logged In</Badge>
                </>
              ) : (
                <>
                  <Wifi className="h-4 w-4 text-green-500" />
                  <Badge variant="success" className="bg-green-500 hover:bg-green-600 text-white">Connected to Suno.ai</Badge>
                </>
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent>
            {error ? (
              <p className="text-xs">{error}</p>
            ) : (
              <p className="text-xs">
                {connected 
                  ? (logged_in 
                      ? "Successfully connected and logged into Suno.ai" 
                      : "Connected to browser but not logged into Suno.ai")
                  : "Browser automation is not connected"}
              </p>
            )}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
};

export default ConnectionStatus;
