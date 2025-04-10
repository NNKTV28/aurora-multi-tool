import os
import subprocess
import platform
from pathlib import Path
import sys
from time import sleep

def clear_screen():
    """Clear terminal screen based on OS"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def print_header():
    """Print tool header"""
    clear_screen()
    print("=" * 50)
    print("           Aurora Multi-Tool v1.1")
    print("=" * 50)
    print()

def run_tool(script_name, tool_name):
    """Run a tool script with error handling"""
    try:
        tool_path = os.path.join("tools", script_name)
        if not os.path.exists(tool_path):
            raise FileNotFoundError(f"Tool script not found: {tool_path}")
        
        print(f"\nRunning {tool_name}...")
        print("-" * 30)
        
        subprocess.run([sys.executable, tool_path], check=True)
        
        print("\nOperation completed successfully!")
        input("\nPress Enter to continue...")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        input("\nPress Enter to continue...")
    except subprocess.CalledProcessError:
        print(f"\nError: Failed to run {tool_name}")
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        input("\nPress Enter to continue...")

def validate_environment():
    """Validate required directories and files exist"""
    if not os.path.exists("tools"):
        os.makedirs("tools")
    
    required_files = [
        "tools/clean_cache.py",
        "tools/backup_browser.py",
        "tools/update_drivers.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("Error: Missing required files:")
        for f in missing_files:
            print(f"- {f}")
        input("\nPress Enter to exit...")
        sys.exit(1)

def show_menu():
    """Display the main menu and get user choice"""
    options = {
        "1": ("Clean Browser Cache", "clean_cache.py"),
        "2": ("Backup Browser Data", "backup_browser.py"),
        "3": ("Restore Browser Backup", "restore_browser_backup.py"),
        "4": ("Update System Drivers", "update_drivers.py"),
        "5": ("System Information", "system_info.py"),
        "6": ("Settings Manager", "settings_manager.py"),
        "7": ("Generate Random String", "generate_random_string.py"),  # New tool added here
        "8": ("Exit", None)
    }
    
    while True:
        print_header()
        print("Available Tools:")
        print("-" * 20)
        
        for key, (name, _) in options.items():
            print(f"{key}. {name}")
        
        choice = input("\nSelect an option (1-8): ").strip()
        
        if choice in options:
            tool_name, script_name = options[choice]
            
            if choice == "8":
                print("\nThank you for using Aurora Multi-Tool!")
                sleep(1.5)
                sys.exit(0)
                
            run_tool(script_name, tool_name)
        else:
            print("\nInvalid choice. Please try again.")
            sleep(1.5)

def main():
    try:
        validate_environment()
        show_menu()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
