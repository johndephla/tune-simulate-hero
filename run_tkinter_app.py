
import tkinter as tk
from tkinter_interface import SunoAutomationGUI
import logging
import os
import sys

# Configure logging with timestamps and both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_automation.log"),
        logging.StreamHandler()
    ]
)

# Create a simple splash screen to indicate the app is loading
def show_splash_screen():
    splash = tk.Tk()
    splash.title("Loading Suno Automation")
    splash.geometry("400x200")
    
    # Center on screen
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 200) // 2
    splash.geometry(f"400x200+{x}+{y}")
    
    splash.configure(bg="#2e2e2e")
    
    # Add loading message
    loading_label = tk.Label(
        splash, 
        text="Loading Suno Automation...\nPlease wait while we initialize Playwright.",
        font=("Arial", 12),
        bg="#2e2e2e",
        fg="white"
    )
    loading_label.pack(pady=50)
    
    # Update the splash screen
    splash.update()
    
    return splash

if __name__ == "__main__":
    try:
        # Display splash screen while initializing
        splash = show_splash_screen()
        
        # Create the main app window
        root = tk.Tk()
        root.withdraw()  # Hide the main window until it's fully loaded
        
        # Initialize the app
        app = SunoAutomationGUI(root)
        
        # Close the splash screen
        splash.destroy()
        
        # Show the main window
        root.deiconify()
        
        # Start the main loop
        root.mainloop()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}")
        
        # Show error in a simple dialog if tkinter is working
        try:
            error_window = tk.Tk()
            error_window.title("Error Starting Application")
            error_window.geometry("500x300")
            
            # Center on screen
            screen_width = error_window.winfo_screenwidth()
            screen_height = error_window.winfo_screenheight()
            x = (screen_width - 500) // 2
            y = (screen_height - 300) // 2
            error_window.geometry(f"500x300+{x}+{y}")
            
            error_window.configure(bg="#2e2e2e")
            
            # Error message
            tk.Label(
                error_window, 
                text="Error Starting Application",
                font=("Arial", 16, "bold"),
                bg="#2e2e2e",
                fg="red"
            ).pack(pady=(20, 10))
            
            # Error details
            error_text = tk.Text(error_window, height=10, width=50, bg="#3e3e3e", fg="white")
            error_text.pack(padx=20, pady=10)
            error_text.insert(tk.END, f"Error: {str(e)}\n\nPlease check if:\n- Chrome is installed\n- You have correct configurations in .env file\n- Your system meets the requirements")
            error_text.config(state="disabled")
            
            # Close button
            tk.Button(
                error_window, 
                text="Close", 
                command=error_window.destroy,
                bg="#555555",
                fg="white",
                font=("Arial", 12)
            ).pack(pady=20)
            
            error_window.mainloop()
        except:
            # If even the error window fails, just print to console
            print(f"CRITICAL ERROR: {str(e)}")
            print("Could not display error dialog. Check the logs for more information.")
