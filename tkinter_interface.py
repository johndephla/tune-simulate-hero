import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import logging
import platform
import webbrowser
from playwright_automation import SunoAutomation
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
        self.root.title("Suno.com Automation")
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
        
        # Inizializzare Playwright in un thread separato
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
        
        title_label = ttk.Label(header_frame, text="Suno.com Automation", style='Header.TLabel')
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(header_frame, text="Genera automaticamente canzoni con Suno.com tramite Selenium")
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
        
        prompt_label = ttk.Label(prompt_frame, text="Describe the song you want:")
        prompt_label.pack(anchor=tk.W)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6)
        self.prompt_text.pack(fill=tk.X, pady=2)
        self.prompt_text.insert(tk.END, "Una canzone su un astronauta che esplora lo spazio")
        
        # Stile musicale
        style_frame = ttk.Frame(left_frame)
        style_frame.pack(fill=tk.X, pady=5)
        
        style_label = ttk.Label(style_frame, text="Stile musicale (opzionale):")
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
        instrumental_check = ttk.Checkbutton(options_frame, text="Strumentale (senza voce)", variable=self.instrumental_var)
        instrumental_check.pack(anchor=tk.W)
        
        self.download_var = tk.BooleanVar(value=True)
        download_check = ttk.Checkbutton(options_frame, text="Scarica canzone al termine", variable=self.download_var)
        download_check.pack(anchor=tk.W)
        
        # Pulsante debug Suno.com
        open_suno_button = ttk.Button(left_frame, text="Apri Suno.com nel browser", command=self.open_suno_website)
        open_suno_button.pack(pady=2)
        
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
    
    def open_suno_website(self):
        """Open Suno.com in the default browser"""
        webbrowser.open("https://suno.com/create?wid=default")
        self.log_message("Suno.com opened in the default browser")
    
    def initialize_automation(self):
        """Initializes the Playwright automation module in a separate thread"""
        self.log_message("Initializing Playwright...")
        
        try:
            # Verify Chrome version
            try:
                chrome_version = self.get_chrome_version()
                if chrome_version:
                    self.log_message(f"Chrome version: {chrome_version}")
                else:
                    self.log_message("Unable to determine Chrome version automatically")
            except Exception as e:
                self.log_message(f"Unable to determine Chrome version: {str(e)}")
            
            use_chrome_profile = self.config.get("USE_CHROME_PROFILE", True)
            chrome_user_data_dir = self.config.get("CHROME_USER_DATA_DIR")
            headless = self.config.get("HEADLESS", "False").lower() == "true"
            
            self.log_message(f"Chrome profile: {use_chrome_profile}")
            self.log_message(f"Chrome profile dir: {chrome_user_data_dir}")
            self.log_message(f"Headless mode: {headless}")
            
            # Try to create the automation
            if use_chrome_profile and chrome_user_data_dir:
                self.log_message(f"Using Chrome profile: {chrome_user_data_dir}")
                self.automation = SunoAutomation(
                    headless=headless,
                    use_chrome_profile=True,
                    chrome_user_data_dir=chrome_user_data_dir
                )
            elif self.config.get("EMAIL") and self.config.get("PASSWORD"):
                self.log_message("Using email/password credentials")
                self.automation = SunoAutomation(
                    email=self.config.get("EMAIL"),
                    password=self.config.get("PASSWORD"),
                    headless=headless
                )
            else:
                self.log_message("Attempting with default Chrome profile")
                self.automation = SunoAutomation(
                    headless=headless,
                    use_chrome_profile=True,
                    chrome_user_data_dir=chrome_user_data_dir
                )
            
            if self.automation.connected:
                self.root.after(0, self.update_status, True, "Playwright connected")
                self.log_message("Initialization completed successfully!")
                
                # Attempt login
                self.log_message("Attempting automatic login...")
                if self.automation.login():
                    self.log_message("Login successful!")
                else:
                    self.log_message("Login failed or already logged in")
            else:
                error_message = self.automation.connection_error if hasattr(self.automation, 'connection_error') and self.automation.connection_error else "Unknown error"
                self.root.after(0, self.update_status, False, f"Error: {error_message}")
                self.log_message(f"Playwright connection error: {error_message}")
                self.show_error_message(error_message)
        except Exception as e:
            error_message = str(e)
            self.root.after(0, self.update_status, False, f"Error: {error_message}")
            self.log_message(f"Error during initialization: {error_message}")
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
        """Show an error message in a dialog"""
        error_info = "Unknown error"
        solutions = [
            "1. Make sure Chrome is installed and updated",
            "2. Verify that the Chrome profile path is correct in the .env file",
            "3. If using an existing Chrome profile, close all Chrome instances",
            "4. Try running the application without the Chrome profile (modify USE_CHROME_PROFILE=False in the .env file)",
            "5. Check if Playwright is installed correctly (pip install playwright && playwright install)"
        ]
        
        # Analyze the error to provide more specific messages
        if "not a valid Win32 application" in error_message:
            error_info = "The Playwright browser executable is not compatible with your Chrome version or operating system"
            solutions = [
                "1. Use 'pip install playwright' to install Playwright",
                "2. Run 'playwright install' to install the browser binaries",
                "3. Make sure you have the correct Python architecture (32-bit or 64-bit)",
                "4. Try reinstalling Playwright: 'pip uninstall playwright && pip install playwright && playwright install'"
            ]
        elif "Browser was not found" in error_message:
            error_info = "Playwright couldn't find the browser installation"
            solutions = [
                "1. Run 'playwright install' to install the browser binaries",
                "2. Make sure Chrome is installed on your system",
                "3. Try specifying a direct path to the browser executable"
            ]
        elif "Timeout" in error_message:
            error_info = "Playwright operation timed out"
            solutions = [
                "1. Check your internet connection",
                "2. Increase the timeout values in the code",
                "3. Try running in non-headless mode to debug visually"
            ]
        
        self.root.after(0, lambda: messagebox.showerror("Connection Error", 
            f"Unable to connect to Playwright: {error_message}\n\n" +
            f"Problem: {error_info}\n\n" +
            "Possible solutions:\n" + "\n".join(solutions)
        ))
    
    def update_status(self, connected, message):
        """Update the status indicator in the GUI"""
        if connected:
            self.status_indicator.config(text="✅", foreground="green")
        else:
            self.status_indicator.config(text="❌", foreground="red")
        
        self.status_label.config(text=message)
    
    def log_message(self, message):
        """Add a message to the log area"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        logging.info(message)
    
    def generate_song(self):
        """Handle song generation"""
        if not self.automation or not self.automation.connected:
            messagebox.showerror("Error", "Playwright is not connected. Check the logs.")
            return
        
        # Get input values from the GUI
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a description for the song")
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
        
        # Disable controls during generation
        self.toggle_controls(False)
        self.progress_var.set(0)
        
        # Start the progress bar
        self.animate_progress()
        
        # Start generation in a separate thread
        gen_thread = threading.Thread(
            target=self._generate_song_thread, 
            args=(prompt, style, title, instrumental, download)
        )
        gen_thread.daemon = True
        gen_thread.start()
    
    def _generate_song_thread(self, prompt, style, title, instrumental, download):
        """Separate thread for song generation"""
        try:
            self.log_message(f"Generating song: {title if title else prompt[:30]}...")
            self.log_message(f"Style: {style if style else 'Not specified'}")
            self.log_message(f"Instrumental: {'Yes' if instrumental else 'No'}")
            
            # Generate the song - passing the explicit parameters
            result = self.automation.generate_song(
                prompt=prompt,
                style=style if style else None,
                title=title if title else None,
                instrumental=instrumental
            )
            
            self.log_message(f"Generation result: {result}")
            
            if result["success"]:
                self.log_message(f"Song generated successfully!")
                self.log_message(f"URL: {result['url']}")
                
                # Download if requested
                if download:
                    self.log_message("Downloading song...")
                    download_result = self.automation.download_song(result["url"])
                    
                    if download_result["success"]:
                        result["file_path"] = download_result["file_path"]
                        self.log_message(f"Song downloaded to: {download_result['file_path']}")
                    else:
                        self.log_message(f"Error during download: {download_result.get('error', 'Unknown error')}")
                
                # Add to history
                self.root.after(0, self.add_to_history, result)
            else:
                self.log_message(f"Error during generation: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
        finally:
            # Re-enable controls
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
