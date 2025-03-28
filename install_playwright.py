
#!/usr/bin/env python3
"""
Installation script for Playwright and its dependencies.
Run this script after installing the Python packages to set up the browser binaries.
"""

import os
import sys
import subprocess
import platform

def main():
    print("Setting up Playwright for Suno.ai Automation...")
    
    # Check if Playwright is installed
    try:
        import playwright
        print("✅ Playwright package is installed.")
    except ImportError:
        print("❌ Playwright package is not installed.")
        print("Installing Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    
    # Install browser binaries
    print("\nInstalling browser binaries (this may take a few minutes)...")
    try:
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                               check=True, capture_output=True, text=True)
        print("✅ Browser binaries installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install browser binaries: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    
    print("\nPlaywright setup completed successfully!")
    print("\nYou can now run the application with:")
    if platform.system() == "Windows":
        print("  python run_tkinter_app.py")
    else:
        print("  python3 run_tkinter_app.py")

if __name__ == "__main__":
    main()
