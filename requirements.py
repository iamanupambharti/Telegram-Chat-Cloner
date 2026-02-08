import subprocess
import sys

def install_packages():
    packages = [
        "customtkinter",
        "telethon"
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)
    print("All required packages installed successfully.")

if __name__ == "__main__":
    install_packages()
