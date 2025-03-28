
import tkinter as tk
from tkinter_interface import SunoAutomationGUI
import logging

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_automation.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    root = tk.Tk()
    app = SunoAutomationGUI(root)
    root.mainloop()
