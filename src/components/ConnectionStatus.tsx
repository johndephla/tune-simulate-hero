
import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

const ConnectionStatus = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState<boolean>(true);
  
  useEffect(() => {
    const checkConnection = async () => {
      setIsChecking(true);
      try {
        // Try to connect to Selenium by making a request to check its status
        const response = await fetch('http://localhost:8000/status', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setIsConnected(data.connected);
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        console.error("Error checking Selenium connection:", error);
        setIsConnected(false);
      } finally {
        setIsChecking(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  if (isChecking && isConnected === null) {
    return (
      <Badge variant="outline" className="px-3 py-1">
        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
        Checking Selenium...
      </Badge>
    );
  }
  
  return isConnected ? (
    <Badge variant="success" className="px-3 py-1">
      Selenium Connected
    </Badge>
  ) : (
    <Badge variant="destructive" className="px-3 py-1">
      Selenium Disconnected
    </Badge>
  );
};

export default ConnectionStatus;
