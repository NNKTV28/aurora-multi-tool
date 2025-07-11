name = "Restore Browser Backup"

def main():
    import os
    import shutil
    import logging
    from pathlib import Path
    from datetime import datetime
    from typing import Dict, List, Optional
    from concurrent.futures import ThreadPoolExecutor
    import platform
    from tqdm import tqdm
    class BrowserRestore:
        def __init__(self):
            self.setup_logging()
            self.source_backup = None
            self.browsers_to_restore = {}

        def setup_logging(self):
            """Configure logging system"""
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = (
                log_dir / f'browser_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            )
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
            )
            self.logger = logging.getLogger(__name__)

        def list_available_backups(self) -> List[Path]:
            """List all available backup directories"""
            backup_root = Path(__file__).parent.parent / "backups"
            if not backup_root.exists():
                return []

            return sorted(
                [d for d in backup_root.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

        def select_backup(self) -> Optional[Path]:
            """Let user select which backup to restore"""
            backups = self.list_available_backups()
            if not backups:
                print("No backups found!")
                return None

            print("\nAvailable backups:")
            for i, backup in enumerate(backups, 1):
                timestamp = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"{i}. {backup.name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})")

            while True:
                try:
                    choice = int(input("\nSelect backup to restore (number): ").strip())
                    if 1 <= choice <= len(backups):
                        return backups[choice - 1]
                    print("Invalid choice, please try again")
                except ValueError:
                    print("Please enter a valid number")

        def select_browsers(self):
            """Let user select which browsers to restore"""
            if not self.source_backup:
                return

            available_browsers = [
                d
                for d in self.source_backup.iterdir()
                if d.is_dir() and d.name not in [".git", "__pycache__"]
            ]

            print("\nSelect browsers to restore:")
            for i, browser in enumerate(available_browsers, 1):
                print(f"{i}. {browser.name}")
            print("A. All browsers")

            choice = (
                input("\nEnter numbers (comma-separated) or 'A' for all: ").strip().upper()
            )

            if choice == "A":
                self.browsers_to_restore = {b.name: b for b in available_browsers}
                return

            try:
                selections = [int(x.strip()) for x in choice.split(",")]
                self.browsers_to_restore = {
                    available_browsers[i - 1].name: available_browsers[i - 1]
                    for i in selections
                    if 1 <= i <= len(available_browsers)
                }
            except ValueError:
                print("Invalid input, restoring all browsers")
                self.browsers_to_restore = {b.name: b for b in available_browsers}

        def get_browser_paths(self) -> Dict[str, Path]:
            """Get current browser installation paths"""
            system = platform.system()
            paths = {}

            if system == "Windows":
                app_data = Path(os.getenv("LOCALAPPDATA", ""))
                roaming = Path(os.getenv("APPDATA", ""))

                paths = {
                    "chrome": app_data / "Google/Chrome/User Data",
                    "firefox": roaming / "Mozilla/Firefox/Profiles",
                    "edge": app_data / "Microsoft/Edge/User Data",
                    "brave": app_data / "BraveSoftware/Brave-Browser/User Data",
                    "opera": roaming / "Opera Software/Opera Stable",
                    "operagx": roaming / "Opera Software/Opera GX Stable",
                    "vivaldi": app_data / "Vivaldi/User Data",
                }
            # Add Linux and MacOS paths if needed

            return {k: v for k, v in paths.items() if v.exists()}

        def restore_browser(
            self, browser_name: str, source_path: Path, dest_path: Path
        ) -> bool:
            """Restore a single browser's data"""
            try:
                if not source_path.exists():
                    self.logger.error(f"Source path does not exist: {source_path}")
                    return False

                # Count files for progress bar
                total_files = sum(1 for _ in source_path.rglob("*") if _.is_file())

                with tqdm(total=total_files, desc=f"Restoring {browser_name}") as pbar:
                    for src_file in source_path.rglob("*"):
                        if src_file.is_file():
                            rel_path = src_file.relative_to(source_path)
                            dst_file = dest_path / rel_path

                            try:
                                dst_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(src_file, dst_file)
                                pbar.update(1)
                            except Exception as e:
                                self.logger.error(f"Error restoring {src_file}: {e}")

                return True
            except Exception as e:
                self.logger.error(f"Failed to restore {browser_name}: {e}")
                return False

        def run(self):
            """Main restore execution"""
            self.logger.info("Starting browser restore process")

            self.source_backup = self.select_backup()
            if not self.source_backup:
                print("No backup selected. Exiting.")
                return False

            self.select_browsers()
            if not self.browsers_to_restore:
                print("No browsers selected. Exiting.")
                return False

            browser_paths = self.get_browser_paths()
            results = {}

            try:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {}
                    for browser, source in self.browsers_to_restore.items():
                        if browser in browser_paths:
                            futures[
                                executor.submit(
                                    self.restore_browser,
                                    browser,
                                    source,
                                    browser_paths[browser],
                                )
                            ] = browser

                    for future in futures:
                        browser = futures[future]
                        try:
                            results[browser] = future.result()
                        except Exception as e:
                            self.logger.error(f"Error restoring {browser}: {e}")
                            results[browser] = False

                return all(results.values())
            except Exception as e:
                self.logger.error(f"Restore process failed: {e}")
                return False



    restore = BrowserRestore()
    if restore.run():
        print("\nRestore completed successfully!")
    else:
        print("\nRestore completed with errors. Check the logs for details.")


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
