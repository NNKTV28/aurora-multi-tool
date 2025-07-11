name = "Backup Browser Data"

def main():
    import os
    import shutil
    import platform
    from pathlib import Path
    import logging
    from datetime import datetime
    import json
    from tqdm import tqdm
    import time
    import hashlib
    from concurrent.futures import ThreadPoolExecutor
    from typing import Dict, List
    
    
    class BrowserBackup:
        def __init__(self):
            self.setup_logging()
            self.load_config()
            self.backup_root = self._create_backup_dir()
    
        def setup_logging(self):
            """Configure logging system"""
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
    
            log_file = (
                log_dir / f'browser_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            )
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
            )
            self.logger = logging.getLogger(__name__)
    
        def load_config(self):
            """Load configuration from JSON file"""
            config_path = Path("config/browser_backup_config.json")
            default_config = {
                "max_workers": 4,
                "verify_copies": True,
                "compression": True,
                "retention_days": 30,
                "excluded_files": [".lock", "Cache", "GPUCache", "CacheDictionary"],
                "browsers": {
                    "chrome": True,
                    "firefox": True,
                    "edge": True,
                    "brave": True,
                    "opera": True,
                    "vivaldi": True,
                },
                "backup_options": {
                    "bookmarks": True,
                    "history": True,
                    "passwords": True,
                    "extensions": True,
                    "cookies": True,
                    "preferences": True,
                },
            }
    
            try:
                if config_path.exists():
                    with open(config_path) as f:
                        self.config = {**default_config, **json.load(f)}
                else:
                    self.config = default_config
                    os.makedirs(config_path.parent, exist_ok=True)
                    with open(config_path, "w") as f:
                        json.dump(default_config, f, indent=4)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                self.config = default_config
    
        def _create_backup_dir(self) -> Path:
            """Create timestamped backup directory"""
            # Get the project root path (parent directory of 'tools')
            backup_root = Path(__file__).parent.parent / "backups"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            return backup_dir
    
        def get_browser_paths(self) -> Dict[str, List[str]]:
            """Get browser paths with improved detection"""
            system = platform.system()
            paths = {}
    
            if system == "Windows":
                paths = self._get_windows_paths()
            elif system == "Linux":
                paths = self._get_linux_paths()
            elif system == "Darwin":
                paths = self._get_macos_paths()
    
            return self._validate_paths(paths)
    
        def _get_windows_paths(self) -> Dict[str, List[str]]:
            """Get browser paths for Windows"""
            app_data = Path(os.getenv("LOCALAPPDATA", ""))
            roaming = Path(os.getenv("APPDATA", ""))
    
            paths = {
                "chrome": [
                    app_data / "Google/Chrome/User Data",
                ],
                "firefox": [
                    roaming / "Mozilla/Firefox/Profiles",
                ],
                "edge": [
                    app_data / "Microsoft/Edge/User Data",
                ],
                "brave": [
                    app_data / "BraveSoftware/Brave-Browser/User Data",
                ],
                "opera": [
                    roaming / "Opera Software/Opera Stable",
                ],
                "operagx": [
                    roaming / "Opera Software/Opera GX Stable",
                ],
                "vivaldi": [
                    app_data / "Vivaldi/User Data",
                ],
            }
    
            return {k: [str(p) for p in v if p.exists()] for k, v in paths.items()}
    
        def _get_linux_paths(self) -> Dict[str, List[str]]:
            """Get browser paths for Linux"""
            home = Path.home()
    
            paths = {
                "chrome": [
                    home / ".config/google-chrome",
                    home / ".config/chromium",
                ],
                "firefox": [
                    home / ".mozilla/firefox",
                ],
                "brave": [
                    home / ".config/BraveSoftware/Brave-Browser",
                ],
                "opera": [
                    home / ".config/opera",
                ],
                "operagx": [
                    home / ".config/opera-gx",
                ],
                "vivaldi": [
                    home / ".config/vivaldi",
                ],
            }
    
            return {k: [str(p) for p in v if p.exists()] for k, v in paths.items()}
    
        def _get_macos_paths(self) -> Dict[str, List[str]]:
            """Get browser paths for macOS"""
            home = Path.home()
    
            paths = {
                "chrome": [
                    home / "Library/Application Support/Google/Chrome",
                ],
                "firefox": [
                    home / "Library/Application Support/Firefox/Profiles",
                ],
                "edge": [
                    home / "Library/Application Support/Microsoft Edge",
                ],
                "brave": [
                    home / "Library/Application Support/BraveSoftware/Brave-Browser",
                ],
                "opera": [
                    home / "Library/Application Support/com.operasoftware.Opera",
                ],
                "operagx": [
                    home / "Library/Application Support/com.operasoftware.OperaGX",
                ],
                "vivaldi": [
                    home / "Library/Application Support/Vivaldi",
                ],
            }
    
            return {k: [str(p) for p in v if p.exists()] for k, v in paths.items()}
    
        def _validate_paths(self, paths: Dict[str, List[str]]) -> Dict[str, List[str]]:
            """Validate and filter browser paths"""
            validated_paths = {}
            for browser, path_list in paths.items():
                if not self.config["browsers"].get(browser, True):
                    continue
                
                validated_paths[browser] = [
                    path
                    for path in path_list
                    if os.path.exists(path)
                    and not any(
                        excluded in path for excluded in self.config["excluded_files"]
                    )
                ]
            return validated_paths
    
        def verify_copy(self, source: Path, destination: Path) -> bool:
            """Verify file copy using SHA256 hash"""
            if not self.config["verify_copies"]:
                return True
    
            try:
                with open(source, "rb") as sf, open(destination, "rb") as df:
                    return (
                        hashlib.sha256(sf.read()).hexdigest()
                        == hashlib.sha256(df.read()).hexdigest()
                    )
            except Exception as e:
                self.logger.error(f"Verification failed: {e}")
                return False
    
        def backup_browser(self, browser_name: str, source_paths: List[str]) -> bool:
            """Backup selected browser data"""
            success = False
            browser_backup_dir = self.backup_root / browser_name
    
            try:
                for source_path in source_paths:
                    source = Path(source_path)
                    if not source.exists():
                        continue
                    
                    dest = browser_backup_dir / source.name
                    dest.mkdir(parents=True, exist_ok=True)
    
                    # Count files for progress bar
                    total_files = sum(
                        1
                        for _, _, files in os.walk(source_path)
                        for f in files
                        if self._should_backup_file(f, browser_name)
                    )
    
                    with tqdm(total=total_files, desc=f"Backing up {browser_name}") as pbar:
                        for root, _, files in os.walk(source_path):
                            rel_path = Path(root).relative_to(source)
                            dest_dir = dest / rel_path
    
                            for file in files:
                                if any(
                                    excluded in file
                                    for excluded in self.config["excluded_files"]
                                ):
                                    continue
                                
                                if not self._should_backup_file(
                                    str(rel_path / file), browser_name
                                ):
                                    continue
                                
                                src_file = Path(root) / file
                                dst_file = dest_dir / file
    
                                try:
                                    dest_dir.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(src_file, dst_file)
                                    if self.verify_copy(src_file, dst_file):
                                        success = True
                                    pbar.update(1)
                                except Exception as e:
                                    self.logger.error(f"Error copying {file}: {e}")
    
            except Exception as e:
                self.logger.error(f"Error backing up {browser_name}: {e}")
    
            return success
    
        def cleanup_old_backups(self):
            """Remove backups older than retention_days"""
            try:
                retention_seconds = self.config["retention_days"] * 24 * 60 * 60
                current_time = time.time()
    
                # Use project root backups folder instead of Documents
                backup_root = Path(__file__).parent.parent / "backups"
                if not backup_root.exists():
                    return
    
                for backup_dir in backup_root.iterdir():
                    if backup_dir.is_dir():
                        dir_time = backup_dir.stat().st_mtime
                        if current_time - dir_time > retention_seconds:
                            shutil.rmtree(backup_dir)
                            self.logger.info(f"Removed old backup: {backup_dir}")
    
            except Exception as e:
                self.logger.error(f"Error cleaning up old backups: {e}")
    
        def run(self):
            """Main backup execution"""
            self.logger.info("Starting browser backup process")
    
            try:
                browser_paths = self.get_browser_paths()
                if not browser_paths:
                    self.logger.warning("No browser profiles found")
                    return
    
                with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
                    futures = {
                        executor.submit(self.backup_browser, browser, paths): browser
                        for browser, paths in browser_paths.items()
                    }
    
                    results = {}
                    for future in futures:
                        browser = futures[future]
                        try:
                            results[browser] = future.result()
                        except Exception as e:
                            self.logger.error(f"Error backing up {browser}: {e}")
                            results[browser] = False
    
                self.cleanup_old_backups()
                self._save_backup_report(results)
    
            except Exception as e:
                self.logger.error(f"Backup process failed: {e}")
                return False
    
            return True
    
        def _save_backup_report(self, results: Dict[str, bool]):
            """Save backup results to a JSON report"""
            report = {
                "timestamp": datetime.now().isoformat(),
                "backup_location": str(self.backup_root),
                "results": results,
            }
    
            report_file = self.backup_root / "backup_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=4)
    
        def _get_browser_data_patterns(self) -> Dict[str, Dict[str, List[str]]]:
            """Define patterns for different types of browser data"""
            return {
                "chrome_based": {  # Chrome, Edge, Brave, Vivaldi
                    "bookmarks": ["Bookmarks", "Bookmarks.bak"],
                    "history": ["History", "Visited Links"],
                    "passwords": ["Login Data", "Login Data-journal"],
                    "extensions": ["Extensions/*"],
                    "cookies": ["Cookies", "Cookies-journal"],
                    "preferences": ["Preferences", "Secure Preferences"],
                },
                "firefox": {
                    "bookmarks": ["places.sqlite", "bookmarkbackups/*"],
                    "history": ["places.sqlite", "places.sqlite-wal"],
                    "passwords": ["logins.json", "key4.db"],
                    "extensions": ["extensions/*", "extensions.json"],
                    "cookies": ["cookies.sqlite"],
                    "preferences": ["prefs.js", "user.js"],
                },
                "opera": {
                    "bookmarks": ["Bookmarks", "Bookmarks.bak"],
                    "history": ["History", "Visited Links"],
                    "passwords": ["Login Data", "Login Data-journal"],
                    "extensions": ["Extensions/*"],
                    "cookies": ["Cookies", "Cookies-journal"],
                    "preferences": ["Preferences"],
                },
                "operagx": {  # Add OperaGX patterns
                    "bookmarks": ["Bookmarks", "Bookmarks.bak"],
                    "history": ["History", "Visited Links"],
                    "passwords": ["Login Data", "Login Data-journal"],
                    "extensions": ["Extensions/*"],
                    "cookies": ["Cookies", "Cookies-journal"],
                    "preferences": ["Preferences", "GX Settings"],
                },
            }
    
        def _should_backup_file(self, file_name: str, browser_type: str) -> bool:
            """Check if a file should be backed up based on selected options"""
            patterns = self._get_browser_data_patterns()
            browser_family = (
                "firefox"
                if "firefox" in browser_type.lower()
                else "opera"
                if "opera" in browser_type.lower()
                else "chrome_based"
            )
    
            if not any(self.config["backup_options"].values()):
                return True  # Backup everything if no specific options selected
    
            for data_type, enabled in self.config["backup_options"].items():
                if not enabled:
                    continue
                
                patterns_for_type = patterns[browser_family][data_type]
                for pattern in patterns_for_type:
                    if pattern.endswith("/*"):
                        if pattern[:-2] in file_name:
                            return True
                    elif pattern in file_name:
                        return True
            return False
    
        def select_backup_options(self):
            """Interactive menu for selecting backup options"""
            print("\nSelect data to backup:")
            print("1. Everything")
            print("2. Custom selection")
    
            choice = input("\nEnter your choice (1-2): ").strip()
    
            if choice == "1":
                for option in self.config["backup_options"]:
                    self.config["backup_options"][option] = True
            elif choice == "2":
                print("\nSelect data types to backup (y/n):")
                for option in self.config["backup_options"]:
                    response = input(f"Backup {option}? (y/n): ").lower()
                    self.config["backup_options"][option] = response.startswith("y")
            else:
                print("Invalid choice, backing up everything")
                for option in self.config["backup_options"]:
                    self.config["backup_options"][option] = True



    backup = BrowserBackup()
    backup.select_backup_options()
    if backup.run():
        print("\nBackup completed successfully!")
        print(f"Backup location: {backup.backup_root}")
    else:
        print("\nBackup completed with errors. Check the logs for details.")

def check_platform_compatibility():
    supported = True
    warnings = []
    try:
        import tqdm
    except:
        supported = False
        warnings.append("Dependency 'tqdm' is missing")
    
    import platform
    if not platform.system() in ["Windows", "Linux", "Darwin"]:
        supported = False
        warnings.append("Platform not supported")

    return supported, warnings
