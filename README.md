
# Suno.ai Automation

Un'applicazione per automatizzare la generazione di canzoni tramite Suno.ai usando Selenium.

## Requisiti

- Python 3.8+
- Chrome Browser
- Pacchetti Python (vedi `requirements.txt`)

## Installazione

1. Clona questo repository
2. Installa le dipendenze:
```
pip install -r requirements.txt
```

## Configurazione

Crea un file `.env` nella directory principale con le seguenti variabili:

```
# Usa il profilo Chrome esistente (raccomandato)
USE_CHROME_PROFILE=True
CHROME_USER_DATA_DIR=C:\Users\tuoutente\AppData\Local\Google\Chrome\User Data

# Oppure usa email e password (alternativa)
EMAIL=tuo_indirizzo@email.com
PASSWORD=tua_password

# Altre opzioni
HEADLESS=False  # Usa True per eseguire Chrome in background
```

## Utilizzo

### Interfaccia Grafica Tkinter

Esegui l'applicazione desktop con:

```
python run_tkinter_app.py
```

L'interfaccia ti permette di:
- Generare canzoni con Suno.ai
- Vedere lo stato della connessione a Selenium
- Visualizzare una cronologia delle canzoni generate
- Aprire le canzoni nel browser o riprodurre i file scaricati

## Risoluzione dei Problemi comuni

### Errore ChromeDriver

Se ricevi l'errore "Failed to initialize Chrome driver" oppure "%1 is not a valid Win32 application", segui questi passaggi:

1. **Verifica la versione di Chrome**
   - Usa il pulsante "Verifica Versione Chrome" nell'interfaccia
   - Oppure apri Chrome e vai a `chrome://version`

2. **Scarica manualmente il ChromeDriver corretto**
   - Vai su [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Scarica la versione che corrisponde alla tua versione di Chrome
   - Estrai il file zip scaricato

3. **Installa il ChromeDriver**
   - Crea una cartella chiamata `chromedriver` nella tua home directory
   - Su Windows: `C:\Users\<tuoutente>\chromedriver`
   - Su macOS/Linux: `~/chromedriver`
   - Posiziona il file chromedriver.exe (Windows) o chromedriver (macOS/Linux) nella cartella

4. **Riavvia l'applicazione**

### Altri problemi

- **Chrome già in esecuzione**: Chiudi tutte le istanze di Chrome prima di avviare l'applicazione
- **Problemi di permessi**: Esegui l'applicazione con privilegi di amministratore
- **Antivirus blocca l'esecuzione**: Aggiungi un'eccezione per chromedriver.exe nel tuo antivirus

## Note Importanti

- È necessario avere un account Suno.ai
- L'automazione funziona meglio utilizzando un profilo Chrome esistente già loggato su Suno.ai
- La prima volta che esegui l'applicazione, potrebbe essere necessario completare manualmente il login
