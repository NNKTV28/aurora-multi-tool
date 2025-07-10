name = "Clean Browser Cache"

def main():
    import os
    import shutil
    from pathlib import Path
    import platform


    def get_cache_paths():
        """Get default cache paths based on OS"""
        system = platform.system()
        user_home = str(Path.home())

        if system == "Windows":
            local_app_data = os.getenv("LOCALAPPDATA")
            app_data = os.getenv("APPDATA")

            paths = {
                "windows_temp": os.environ.get("TEMP"),
                "chrome": f"{local_app_data}\\Google\\Chrome\\User Data\\Default\\Cache",
                "edge": f"{local_app_data}\\Microsoft\\Edge\\User Data\\Default\\Cache",
                "opera_gx": f"{app_data}\\Opera Software\\Opera GX Stable\\Cache",
                "brave": f"{local_app_data}\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Cache",
            }

        elif system == "Linux":
            paths = {
                "system_temp": "/tmp",
                "chrome": f"{user_home}/.cache/google-chrome",
                "edge": f"{user_home}/.cache/microsoft-edge",
                "opera_gx": f"{user_home}/.cache/opera",
                "brave": f"{user_home}/.cache/BraveSoftware/Brave-Browser",
            }

        elif system == "Darwin":  # macOS
            paths = {
                "system_temp": "/private/tmp",
                "chrome": f"{user_home}/Library/Caches/Google/Chrome",
                "edge": f"{user_home}/Library/Caches/Microsoft Edge",
                "opera_gx": f"{user_home}/Library/Caches/com.operasoftware.OperaGX",
                "brave": f"{user_home}/Library/Caches/BraveSoftware/Brave-Browser",
            }

        return paths


    def clean_directory(path):
        """Clean a directory while preserving the directory itself"""
        if not os.path.exists(path):
            return 0

        bytes_freed = 0
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    bytes_freed += os.path.getsize(item_path)
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    bytes_freed += get_directory_size(item_path)
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error cleaning {item_path}: {str(e)}")

        return bytes_freed


    def get_directory_size(path):
        """Calculate total size of a directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception:
                    pass
        return total_size


    def format_size(bytes):
        """Convert bytes to human readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"



    print("Starting cache cleanup...")

    cache_paths = get_cache_paths()
    total_freed = 0

    for location, path in cache_paths.items():
        print(f"\nCleaning {location}...")
        freed = clean_directory(path)
        total_freed += freed
        print(f"Freed up {format_size(freed)}")

    print(f"\nTotal space freed: {format_size(total_freed)}")

def check_platform_compatibility():
    supported = True
    warnings = []

    import platform
    if not platform.system() in ["Windows", "Linux", "Darwin"]:
        supported = False
        warnings.append("Platform not supported")

    return supported, warnings
