import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import logging
import platform
import webbrowser
from browser_automation import SunoAutomation
from config import get_config

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SunoAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Suno.ai Automation")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.automation = None
        self.song_history = []
        self.config = get_config()
        self.progress_running = False
        
        # Caricare icone e stili
        self.setup_styles()
        
        # Creare il layout principale
        self.create_main_layout()
        
        # Inizializzare Selenium in un thread separato
        self.init_thread = threading.Thread(target=self.initialize_automation)
        self.init_thread.daemon = True
        self.init_thread.start()
    
    def setup_styles(self):
        """Configurare gli stili e temi per l'interfaccia"""
        style = ttk.Style()
        style.theme_use('clam')  # Usa un tema moderno
        
        # Configura stile per i pulsanti
        style.configure('TButton', font=('Helvetica', 10), borderwidth=1)
        style.map('TButton', background=[('active', '#3B82F6'), ('!disabled', '#2563EB')])
        
        # Configura stile per le etichette
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        
        # Configura stile per i frame
        style.configure('Card.TFrame', borderwidth=1, relief='solid', background='#FFFFFF')
    
    def create_main_layout(self):
        """Creare il layout principale dell'interfaccia"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Intestazione
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Suno.ai Automation", style='Header.TLabel')
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(header_frame, text="Genera automaticamente canzoni con Suno.ai tramite Selenium")
        subtitle_label.pack(pady=2)
        
        # Indicatore di stato connessione
        self.status_frame = ttk.Frame(header_frame, padding=5)
        self.status_frame.pack(pady=10)
        
        self.status_label = ttk.Label(self.status_frame, text="Connessione a Selenium...")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.status_indicator = ttk.Label(self.status_frame, text="⏳", font=('Helvetica', 12))
        self.status_indicator.pack(side=tk.LEFT)
        
        # Area contenuto principale divisa in due colonne
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Colonna sinistra (form)
        left_frame = ttk.Frame(content_frame, style='Card.TFrame', padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        form_label = ttk.Label(left_frame, text="Genera una nuova canzone", style='Header.TLabel')
        form_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Prompt input
        prompt_frame = ttk.Frame(left_frame)
        prompt_frame.pack(fill=tk.X, pady=5)
        
        prompt_label = ttk.Label(prompt_frame, text="Lyrics:")
        prompt_label.pack(anchor=tk.W)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6)
        self.prompt_text.pack(fill=tk.X, pady=2)
        self.prompt_text.insert(tk.END, "Una canzone su un astronauta che esplora lo spazio")
        
        # Stile musicale
        style_frame = ttk.Frame(left_frame)
        style_frame.pack(fill=tk.X, pady=5)
        
        style_label = ttk.Label(style_frame, text="Stile musicale:")
        style_label.pack(anchor=tk.W)
        
        self.style_entry = ttk.Entry(style_frame)
        self.style_entry.pack(fill=tk.X, pady=2)
        self.style_entry.insert(0, "Rock spaziale, melodico")
        
        # Titolo canzone
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        title_label = ttk.Label(title_frame, text="Titolo (opzionale):")
        title_label.pack(anchor=tk.W)
        
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(fill=tk.X, pady=2)
        self.title_entry.insert(0, "Viaggiando tra le stelle")
        
        # Opzioni aggiuntive
        options_frame = ttk.Frame(left_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.instrumental_var = tk.BooleanVar(value=True)
        instrumental_check = ttk.Checkbutton(options_frame, text="Strumentale", variable=self.instrumental_var)
        instrumental_check.pack(anchor=tk.W)
        
        self.download_var = tk.BooleanVar(value=True)
        download_check = ttk.Checkbutton(options_frame, text="Scarica canzone al termine", variable=self.download_var)
        download_check.pack(anchor=tk.W)
        
        # Pulsante di generazione
        generate_button = ttk.Button(left_frame, text="Genera Canzone", command=self.generate_song)
        generate_button.pack(pady=10)
        
        # Barra di stato
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(left_frame, orient=tk.HORIZONTAL, variable=self.progress_var, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Area log
        log_label = ttk.Label(left_frame, text="Log:")
        log_label.pack(anchor=tk.W, pady=(10, 2))
        
        self.log_text = scrolledtext.ScrolledText(left_frame, height=6, state='disabled')
        self.log_text.pack(fill=tk.X)
        
        # Colonna destra (storico canzoni)
        right_frame = ttk.Frame(content_frame, style='Card.TFrame', padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        history_label = ttk.Label(right_frame, text="Canzoni Generate", style='Header.TLabel')
        history_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Lista delle canzoni generate
        self.history_frame = ttk.Frame(right_frame)
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder per storia vuota
        self.empty_history_label = ttk.Label(self.history_frame, text="Nessuna canzone generata")
        self.empty_history_label.pack(pady=20)
        
        # Pulsanti aggiuntivi per problemi comuni
        help_frame = ttk.Frame(right_frame)
        help_frame.pack(fill=tk.X, pady=5)
        
        download_driver_button = ttk.Button(
            help_frame, 
            text="Scarica ChromeDriver", 
            command=self.open_chromedriver_download
        )
        download_driver_button.pack(fill=tk.X, pady=2)
        
        check_chrome_button = ttk.Button(
            help_frame, 
            text="Verifica Versione Chrome", 
            command=self.check_chrome_version
        )
        check_chrome_button.pack(fill=tk.X, pady=2)
        
        open_log_button = ttk.Button(
            help_frame, 
            text="Apri File di Log", 
            command=self.open_log_file
        )
        open_log_button.pack(fill=tk.X, pady=2)
    
    def initialize_automation(self):
        """Inizializza il modulo di automazione di Selenium in un thread separato"""
        self.log_message("Inizializzazione di Selenium...")
        
        try:
            # Verifica se chromedriver esiste nella directory corrente
            self.log_message(f"Sistema operativo: {platform.system()}")
            
            # Verifica versione di Chrome
            try:
                chrome_version = self.get_chrome_version()
                if chrome_version:
                    self.log_message(f"Versione Chrome: {chrome_version}")
                else:
                    self.log_message("Impossibile determinare la versione di Chrome automaticamente")
            except Exception as e:
                self.log_message(f"Impossibile determinare la versione di Chrome: {str(e)}")
            
            use_chrome_profile = self.config.get("USE_CHROME_PROFILE", True)
            chrome_user_data_dir = self.config.get("CHROME_USER_DATA_DIR")
            headless = self.config.get("HEADLESS", "False").lower() == "true"
            
            self.log_message(f"Chrome profile: {use_chrome_profile}")
            self.log_message(f"Chrome profile dir: {chrome_user_data_dir}")
            self.log_message(f"Headless mode: {headless}")
            
            # Prova a creare l'automazione
            if use_chrome_profile and chrome_user_data_dir:
                self.log_message(f"Utilizzo profilo Chrome: {chrome_user_data_dir}")
                self.automation = SunoAutomation(
                    headless=headless,
                    use_chrome_profile=True,
                    chrome_user_data_dir=chrome_user_data_dir
                )
            elif self.config.get("EMAIL") and self.config.get("PASSWORD"):
                self.log_message("Utilizzo credenziali email/password")
                self.automation = SunoAutomation(
                    email=self.config.get("EMAIL"),
                    password=self.config.get("PASSWORD"),
                    headless=headless
                )
            else:
                self.log_message("Tentativo con il profilo Chrome predefinito")
                self.automation = SunoAutomation(
                    headless=headless,
                    use_chrome_profile=True,
                    chrome_user_data_dir=chrome_user_data_dir
                )
            
            if self.automation.connected:
                self.root.after(0, self.update_status, True, "Selenium connesso")
                self.log_message("Inizializzazione completata con successo!")
                
                # Tentativo di login
                self.log_message("Tentativo di login automatico...")
                if self.automation.login():
                    self.log_message("Login effettuato con successo!")
                else:
                    self.log_message("Login non riuscito o già effettuato")
            else:
                error_message = self.automation.connection_error if hasattr(self.automation, 'connection_error') and self.automation.connection_error else "Errore sconosciuto"
                self.root.after(0, self.update_status, False, f"Errore: {error_message}")
                self.log_message(f"Errore di connessione Selenium: {error_message}")
                self.show_error_message(error_message)
        except Exception as e:
            error_message = str(e)
            self.root.after(0, self.update_status, False, f"Errore: {error_message}")
            self.log_message(f"Errore durante l'inizializzazione: {error_message}")
            self.show_error_message(error_message)
    
    def get_chrome_version(self):
        """Ottieni la versione di Chrome installata"""
        try:
            if platform.system() == "Windows":
                import subprocess
                from subprocess import PIPE
                
                # Primo tentativo: usa il registro di Windows
                try:
                    result = subprocess.run(['reg', 'query', 'HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome', '/v', 'version'], 
                                            stdout=PIPE, stderr=PIPE, text=True, check=False)
                    if result.returncode == 0:
                        # Estrai la versione dall'output
                        for line in result.stdout.split('\n'):
                            if 'version' in line.lower():
                                return line.split()[-1]
                except:
                    pass
                
                # Secondo tentativo: controlla direttamente il file di Chrome
                try:
                    result = subprocess.run(["wmic", "datafile", "where", "name='C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe'", "get", "Version", "/value"], 
                                      stdout=PIPE, stderr=PIPE, text=True, check=False)
                    if result.returncode == 0 and "Version=" in result.stdout:
                        return result.stdout.split("=")[1].strip()
                except:
                    pass
                
                # Terzo tentativo: prova il percorso alternativo
                try:
                    result = subprocess.run(["wmic", "datafile", "where", "name='C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe'", "get", "Version", "/value"], 
                                      stdout=PIPE, stderr=PIPE, text=True, check=False)
                    if result.returncode == 0 and "Version=" in result.stdout:
                        return result.stdout.split("=")[1].strip()
                except:
                    pass
                    
            elif platform.system() == "Darwin":  # macOS
                try:
                    import subprocess
                    result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], 
                                      capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        return result.stdout.strip().split("Chrome ")[1]
                except:
                    pass
            else:  # Linux
                try:
                    import subprocess
                    result = subprocess.run(["google-chrome", "--version"], 
                                      capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        return result.stdout.strip().split("Google Chrome ")[1]
                except:
                    pass
        except Exception as e:
            logger.error(f"Errore nel rilevare la versione di Chrome: {e}")
            
        return None
    
    def open_chromedriver_download(self):
        """Apre la pagina di download di ChromeDriver"""
        webbrowser.open("https://chromedriver.chromium.org/downloads")
        self.log_message("Pagina di download ChromeDriver aperta nel browser")
        
        # Mostra ulteriori istruzioni
        messagebox.showinfo("Download ChromeDriver", 
            "Per scaricare manualmente ChromeDriver:\n\n"
            "1. Determina la versione di Chrome dal pulsante 'Verifica Versione Chrome'\n"
            "2. Scarica la versione corrispondente di ChromeDriver dal sito\n"
            "3. Estrai il file scaricato\n"
            "4. Crea una cartella 'chromedriver' nella tua home directory\n"
            f"5. Copia il file chromedriver.exe nella cartella: {os.path.join(os.path.expanduser('~'), 'chromedriver')}"
        )
    
    def check_chrome_version(self):
        """Verifica e mostra la versione di Chrome installata"""
        version = self.get_chrome_version()
        if version:
            messagebox.showinfo("Versione Chrome", f"La versione di Google Chrome installata è: {version}")
            self.log_message(f"Versione Chrome rilevata: {version}")
        else:
            messagebox.showerror("Errore", "Impossibile determinare la versione di Chrome.\n\n"
                                 "Verifica che Google Chrome sia installato correttamente.")
            self.log_message("Impossibile determinare la versione di Chrome")
    
    def open_log_file(self):
        """Apre il file di log nell'editor predefinito"""
        log_file = "suno_automation.log"
        if os.path.exists(log_file):
            if platform.system() == "Windows":
                os.startfile(log_file)
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.call(['open', log_file])
            else:  # Linux
                import subprocess
                subprocess.call(['xdg-open', log_file])
            self.log_message(f"File di log aperto: {log_file}")
        else:
            messagebox.showerror("Errore", f"File di log non trovato: {log_file}")
    
    def show_error_message(self, error_message):
        """Mostra un messaggio di errore in una finestra di dialogo"""
        error_info = "Errore sconosciuto"
        solutions = [
            "1. Assicurati che Chrome sia installato e aggiornato",
            "2. Verifica che il percorso al profilo Chrome sia corretto nel file .env",
            "3. Se stai usando un profilo Chrome esistente, chiudi tutte le istanze di Chrome",
            "4. Prova a eseguire l'applicazione senza il profilo Chrome (modifica USE_CHROME_PROFILE=False nel file .env)"
        ]
        
        # Analizza l'errore per fornire messaggi più specifici
        if "not a valid Win32 application" in error_message:
            error_info = "Il file ChromeDriver non è compatibile con la tua versione di Chrome o con il sistema operativo"
            solutions = [
                "1. Usa il pulsante 'Verifica Versione Chrome' per controllare la versione installata",
                "2. Usa il pulsante 'Scarica ChromeDriver' per ottenere la versione corretta",
                "3. Assicurati di scaricare ChromeDriver per la tua architettura (32-bit o 64-bit)",
                "4. Crea una cartella 'chromedriver' nella tua home directory e metti lì il file scaricato",
                f"5. Percorso suggerito: {os.path.join(os.path.expanduser('~'), 'chromedriver', 'chromedriver.exe')}"
            ]
        elif "session not created" in error_message and "Chrome version" in error_message:
            error_info = "Versione di ChromeDriver non compatibile con la tua versione di Chrome"
            solutions = [
                "1. Usa il pulsante 'Verifica Versione Chrome' per controllare la versione installata",
                "2. Usa il pulsante 'Scarica ChromeDriver' per ottenere la versione corretta per il tuo Chrome"
            ]
        elif "Chrome failed to start" in error_message:
            error_info = "Chrome non è riuscito ad avviarsi correttamente"
            solutions = [
                "1. Chiudi tutte le istanze di Chrome in esecuzione",
                "2. Controlla se il tuo antivirus blocca Chrome quando viene avviato da Selenium",
                "3. Prova ad eseguire l'applicazione con privilegi di amministratore",
                "4. Disattiva temporaneamente l'opzione USE_CHROME_PROFILE nel file .env"
            ]
        
        self.root.after(0, lambda: messagebox.showerror("Errore di connessione", 
            f"Impossibile connettersi a Selenium: {error_message}\n\n" +
            f"Problema: {error_info}\n\n" +
            "Possibili soluzioni:\n" + "\n".join(solutions)
        ))
    
    def update_status(self, connected, message):
        """Aggiorna l'indicatore di stato nella GUI"""
        if connected:
            self.status_indicator.config(text="✅", foreground="green")
        else:
            self.status_indicator.config(text="❌", foreground="red")
        
        self.status_label.config(text=message)
    
    def log_message(self, message):
        """Aggiunge un messaggio all'area di log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        logger.info(message)
    
    def generate_song(self):
        """Gestisce la generazione di una canzone"""
        if not self.automation or not self.automation.connected:
            messagebox.showerror("Errore", "Selenium non è connesso. Controlla i log.")
            return
        
        # Get input values from the GUI
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Errore", "Inserisci il testo per la canzone (lyrics)")
            return
        
        style = self.style_entry.get().strip()
        title = self.title_entry.get().strip()
        instrumental = self.instrumental_var.get()
        download = self.download_var.get()
        
        # Debug logs to make sure we're getting the correct values
        self.log_message(f"Input - Prompt: '{prompt}'")
        self.log_message(f"Input - Style: '{style}'")
        self.log_message(f"Input - Title: '{title}'")
        self.log_message(f"Input - Instrumental: {instrumental}")
        self.log_message(f"Input - Download: {download}")
        
        # Disabilita i controlli durante la generazione
        self.toggle_controls(False)
        self.progress_var.set(0)
        
        # Avvia la barra di progresso
        self.animate_progress()
        
        # Avvia la generazione in un thread separato
        gen_thread = threading.Thread(
            target=self._generate_song_thread, 
            args=(prompt, style, title, instrumental, download)
        )
        gen_thread.daemon = True
        gen_thread.start()
    
    def _generate_song_thread(self, prompt, style, title, instrumental, download):
        """Thread separato per la generazione della canzone"""
        try:
            self.log_message(f"Generazione canzone: {title if title else prompt[:30]}...")
            self.log_message(f"Stile: {style if style else 'Non specificato'}")
            self.log_message(f"Strumentale: {'Sì' if instrumental else 'No'}")
            
            # Genera la canzone - passing the explicit parameters
            result = self.automation.generate_song(
                prompt=prompt,
                style=style if style else None,
                title=title if title else None,
                instrumental=instrumental
            )
            
            self.log_message(f"Risultato generazione: {result}")
            
            if result["success"]:
                self.log_message(f"Canzone generata con successo!")
                self.log_message(f"URL: {result['url']}")
                
                # Scarica se richiesto
                if download:
                    self.log_message("Scaricamento canzone...")
                    download_result = self.automation.download_song(result["url"])
                    
                    if download_result["success"]:
                        result["file_path"] = download_result["file_path"]
                        self.log_message(f"Canzone scaricata in: {download_result['file_path']}")
                    else:
                        self.log_message(f"Errore durante il download: {download_result.get('error', 'Errore sconosciuto')}")
                
                # Aggiungi alla cronologia
                self.root.after(0, self.add_to_history, result)
            else:
                self.log_message(f"Errore durante la generazione: {result.get('error', 'Errore sconosciuto')}")
        except Exception as e:
            self.log_message(f"Errore: {str(e)}")
        finally:
            # Riattiva i controlli
            self.root.after(0, self.toggle_controls, True)
            self.root.after(0, self.stop_progress)
    
    def animate_progress(self):
        """Anima la barra di progresso"""
        import time
        self.progress_running = True
        
        def _animate():
            if not self.progress_running:
                return
            
            current = self.progress_var.get()
            if current >= 100:
                self.progress_var.set(0)
            else:
                self.progress_var.set(current + 1)
            
            self.root.after(50, _animate)
        
        _animate()
    
    def stop_progress(self):
        """Ferma l'animazione della barra di progresso"""
        self.progress_running = False
        self.progress_var.set(0)
    
    def toggle_controls(self, enabled):
        """Abilita/disabilita i controlli del form"""
        state = 'normal' if enabled else 'disabled'
        
        self.prompt_text.config(state=state)
        self.style_entry.config(state=state)
        self.title_entry.config(state=state)
        
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state)
    
    def add_to_history(self, result):
        """Aggiunge una canzone alla cronologia"""
        # Rimuovi il placeholder se è la prima canzone
        if len(self.song_history) == 0:
            self.empty_history_label.pack_forget()
        
        # Limita la cronologia a 10 elementi
        self.song_history.insert(0, result)
        if len(self.song_history) > 10:
            self.song_history = self.song_history[:10]
        
        # Ricostruisci la lista della cronologia
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        for i, song in enumerate(self.song_history):
            song_frame = ttk.Frame(self.history_frame, style='Card.TFrame', padding=5)
            song_frame.pack(fill=tk.X, pady=5, padx=2)
            
            title_text = song.get('title') or song.get('prompt')[:30] + "..."
            title_label = ttk.Label(song_frame, text=title_text, font=('Helvetica', 10, 'bold'))
            title_label.pack(anchor=tk.W)
            
            if song.get('style'):
                style_label = ttk.Label(song_frame, text=f"Stile: {song['style']}")
                style_label.pack(anchor=tk.W)
            
            url_frame = ttk.Frame(song_frame)
            url_frame.pack(fill=tk.X, pady=2)
            
            url_label = ttk.Label(url_frame, text="URL: ")
            url_label.pack(side=tk.LEFT)
            
            url_entry = ttk.Entry(url_frame)
            url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            url_entry.insert(0, song['url'])
            url_entry.config(state='readonly')
            
            open_button = ttk.Button(song_frame, text="Apri nel browser", 
                                     command=lambda u=song['url']: self.open_url(u))
            open_button.pack(pady=2)
            
            if song.get('file_path'):
                file_button = ttk.Button(song_frame, text="Apri file locale", 
                                        command=lambda f=song['file_path']: self.open_file(f))
                file_button.pack(pady=2)
    
    def open_url(self, url):
        """Apre l'URL nel browser predefinito"""
        import webbrowser
        webbrowser.open(url)
    
    def open_file(self, file_path):
        """Apre il file locale con l'applicazione predefinita"""
        if os.path.exists(file_path):
            import subprocess
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        else:
            messagebox.showerror("Errore", f"Il file non esiste più: {file_path}")
