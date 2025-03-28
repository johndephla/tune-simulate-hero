
import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

const ConnectionStatus = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState<boolean>(true);
  const [simulateConnection, setSimulateConnection] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  useEffect(() => {
    const checkConnection = async () => {
      setIsChecking(true);
      
      if (simulateConnection) {
        setIsConnected(true);
        setIsChecking(false);
        setErrorMessage(null);
        return;
      }
      
      try {
        console.log("Checking Selenium connection status...");
        
        // In un ambiente di sviluppo, prova prima localhost
        let apiUrl = `http://localhost:8000/status`;
        
        // Se siamo in produzione o in un ambiente hosted, potrebbe essere necessario cambiare l'URL
        if (window.location.hostname !== 'localhost') {
          // Prova con il dominio corrente ma sulla porta 8000
          apiUrl = `http://${window.location.hostname}:8000/status`;
        }
        
        console.log("Connecting to API at:", apiUrl);
        
        // Try to connect to Selenium by making a request to check its status
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Importante: timeout per evitare attese troppo lunghe
          signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log("Selenium connection status:", data);
          setIsConnected(data.connected);
          if (data.error) {
            setErrorMessage(data.error);
          } else {
            setErrorMessage(null);
          }
        } else {
          console.error("Failed to get status from server:", response.statusText);
          setIsConnected(false);
          setErrorMessage(`HTTP Error: ${response.status} ${response.statusText}`);
        }
      } catch (error) {
        console.error("Error checking Selenium connection:", error);
        setIsConnected(false);
        setErrorMessage(
          "Non è possibile connettersi al server backend. Assicurati che 'python main.py' sia in esecuzione " +
          "e che la porta 8000 sia accessibile. In un ambiente browser, potresti dover attivare la modalità simulazione."
        );
      } finally {
        setIsChecking(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10 seconds
    
    return () => clearInterval(interval);
  }, [simulateConnection]);
  
  const handleToggleSimulation = () => {
    setSimulateConnection(prev => {
      const newValue = !prev;
      if (newValue) {
        toast.success("Modalità simulazione attivata. La connessione a Selenium è simulata.");
      } else {
        toast.info("Modalità simulazione disattivata. Controllo della connessione reale.");
      }
      return newValue;
    });
  };
  
  if (isChecking && isConnected === null) {
    return (
      <div>
        <Badge variant="outline" className="px-3 py-1 mb-2">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          Checking Selenium...
        </Badge>
        <div className="text-xs">
          <button 
            onClick={handleToggleSimulation} 
            className="text-blue-500 hover:underline"
          >
            {simulateConnection ? "Disattiva simulazione" : "Simula connessione"}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div>
      {isConnected ? (
        <Badge variant="success" className="px-3 py-1 mb-2">
          Selenium Connected
        </Badge>
      ) : (
        <div>
          <Badge variant="destructive" className="px-3 py-1 mb-2">
            Selenium Disconnected
          </Badge>
          {errorMessage && (
            <div className="text-xs text-red-500 max-w-xs mt-1 mb-2">
              {errorMessage}
            </div>
          )}
          <div className="text-xs mt-1 text-gray-600">
            Assicurati di aver avviato "python main.py" e che la porta 8000 sia accessibile.
          </div>
        </div>
      )}
      <div className="text-xs">
        <button 
          onClick={handleToggleSimulation} 
          className="text-blue-500 hover:underline"
        >
          {simulateConnection ? "Disattiva simulazione" : "Simula connessione"}
        </button>
        {simulateConnection && (
          <div className="text-xs text-green-600 mt-1">
            Modalità simulazione attiva. Funzionalità limitate.
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatus;
