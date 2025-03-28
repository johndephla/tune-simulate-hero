
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import logging
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
        
        # Stile musicale
        style_frame = ttk.Frame(left_frame)
        style_frame.pack(fill=tk.X, pady=5)
        
        style_label = ttk.Label(style_frame, text="Stile musicale:")
        style_label.pack(anchor=tk.W)
        
        self.style_entry = ttk.Entry(style_frame)
        self.style_entry.pack(fill=tk.X, pady=2)
        
        # Titolo canzone
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        title_label = ttk.Label(title_frame, text="Titolo (opzionale):")
        title_label.pack(anchor=tk.W)
        
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(fill=tk.X, pady=2)
        
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
    
    def initialize_automation(self):
        """Inizializza il modulo di automazione di Selenium in un thread separato"""
        self.log_message("Inizializzazione di Selenium...")
        
        try:
            use_chrome_profile = self.config.get("USE_CHROME_PROFILE", True)
            chrome_user_data_dir = self.config.get("CHROME_USER_DATA_DIR")
            headless = self.config.get("HEADLESS", "False").lower() == "true"
            
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
                self.root.after(0, self.update_status, False, f"Errore: {self.automation.connection_error}")
                self.log_message(f"Errore di connessione: {self.automation.connection_error}")
        except Exception as e:
            self.root.after(0, self.update_status, False, f"Errore: {str(e)}")
            self.log_message(f"Errore durante l'inizializzazione: {str(e)}")
    
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
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Errore", "Inserisci il testo per la canzone (lyrics)")
            return
        
        style = self.style_entry.get().strip()
        title = self.title_entry.get().strip()
        instrumental = self.instrumental_var.get()
        download = self.download_var.get()
        
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
            
            # Genera la canzone
            result = self.automation.generate_song(
                prompt=prompt,
                style=style if style else None,
                title=title if title else None,
                instrumental=instrumental
            )
            
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SunoAutomationGUI(root)
    root.mainloop()

