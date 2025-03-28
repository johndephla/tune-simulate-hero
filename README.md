
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

### Interfaccia Grafica Tkinter (Raccomandata)

Esegui l'applicazione desktop con:

```
python run_tkinter_app.py
```

L'interfaccia grafica ti permette di:
- Generare canzoni con Suno.ai
- Vedere lo stato della connessione a Selenium
- Visualizzare una cronologia delle canzoni generate
- Aprire le canzoni nel browser o riprodurre i file scaricati

### Interfaccia Web (Alternativa)

Avvia il server API:

```
python main.py
```

Quindi accedi all'interfaccia web all'indirizzo http://localhost:5173

## Note Importanti

- È necessario avere un account Suno.ai
- L'automazione funziona meglio utilizzando un profilo Chrome esistente già loggato su Suno.ai
- La prima volta che esegui l'applicazione, potrebbe essere necessario completare manualmente il login
