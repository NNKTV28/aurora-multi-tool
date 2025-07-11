name = "Update System Drivers"

def main():
    import os
    import sys
    import subprocess
    import winreg
    import requests
    from tqdm import tqdm
    import ctypes
    import logging
    from datetime import datetime
    import json
    from pathlib import Path
    from concurrent.futures import ThreadPoolExecutor


    class DriverUpdater:
        def __init__(self):
            self.setup_logging()
            self.temp_dir = Path(os.environ["TEMP"]) / "driver_updates"
            self.backup_dir = Path(os.environ["USERPROFILE"]) / "DriverBackups"
            self.config = self.load_config()
            self.session = requests.Session()

        def setup_logging(self):
            """Configure logging for the application"""
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = (
                log_dir / f'driver_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            )
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
            )
            self.logger = logging.getLogger(__name__)

        def load_config(self):
            """Load configuration from config file"""
            config_path = Path("config/driver_update_config.json")
            default_config = {
                "api_url": "https://windowsupdate.microsoft.com/catalog/api/drivers",
                "backup_drivers": True,
                "concurrent_updates": 3,
                "retry_attempts": 3,
                "timeout": 30,
            }

            if config_path.exists():
                try:
                    with open(config_path) as f:
                        return {**default_config, **json.load(f)}
                except json.JSONDecodeError:
                    self.logger.error("Invalid config file, using defaults")
                    return default_config
            return default_config

        def backup_current_driver(self, device_id):
            """Backup existing driver before update"""
            try:
                self.backup_dir.mkdir(exist_ok=True)
                backup_file = (
                    self.backup_dir
                    / f"driver_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pbk"
                )

                subprocess.run(
                    ["pnputil", "/export-driver", device_id, str(backup_file)],
                    check=True,
                    capture_output=True,
                )
                self.logger.info(f"Driver backup created: {backup_file}")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to backup driver: {e}")
                return False

        def get_device_ids(self):
            """Get list of device hardware IDs from Windows registry with improved error handling"""
            device_ids = []
            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Enum",
                    0,
                    winreg.KEY_READ,
                ) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    hw_id = winreg.QueryValueEx(subkey, "HardwareID")[0]
                                    if isinstance(hw_id, (list, tuple)):
                                        device_ids.extend(hw_id)
                                    elif hw_id:
                                        device_ids.append(hw_id)
                                except WindowsError:
                                    pass
                            i += 1
                        except WindowsError:
                            break
            except WindowsError as e:
                self.logger.error(f"Error accessing registry: {e}")

            return list(set(device_ids))  # Remove duplicates

        def check_driver_update(self, device_id):
            """Check for driver updates with retry mechanism"""
            for attempt in range(self.config["retry_attempts"]):
                try:
                    response = self.session.get(
                        self.config["api_url"],
                        params={
                            "hwid": device_id,
                            "os": f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}",
                        },
                        timeout=self.config["timeout"],
                    )
                    response.raise_for_status()
                    data = response.json()

                    if data and data.get("drivers"):
                        latest_driver = data["drivers"][0]
                        return {
                            "has_update": True,
                            "download_url": latest_driver["downloadUrl"],
                            "version": latest_driver["version"],
                            "name": latest_driver.get("name", "Unknown Driver"),
                        }
                    break
                except (requests.RequestException, KeyError) as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == self.config["retry_attempts"] - 1:
                        self.logger.error(
                            f"Failed to check updates after {self.config['retry_attempts']} attempts"
                        )

            return {
                "has_update": False,
                "download_url": None,
                "version": None,
                "name": "Unknown Driver",
            }

        def download_driver(self, driver_url, save_path):
            """Download driver file with progress bar and verification"""
            try:
                response = self.session.get(driver_url, stream=True)
                total_size = int(response.headers.get("content-length", 0))

                with open(save_path, "wb") as f, tqdm(
                    total=total_size, unit="B", unit_scale=True
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

                # Verify download
                if os.path.getsize(save_path) != total_size:
                    raise ValueError("Downloaded file size mismatch")

                return True
            except Exception as e:
                self.logger.error(f"Download failed: {e}")
                return False

        def process_device(self, device_id):
            """Process a single device update"""
            self.logger.info(f"Checking updates for device: {device_id}")

            driver_info = self.check_driver_update(device_id)
            if driver_info["has_update"]:
                self.logger.info(
                    f"Update available for {driver_info['name']}: version {driver_info['version']}"
                )

                if self.config["backup_drivers"]:
                    self.backup_current_driver(device_id)

                filename = os.path.basename(driver_info["download_url"])
                save_path = self.temp_dir / filename

                if self.download_driver(driver_info["download_url"], save_path):
                    if self.install_driver(save_path):
                        self.logger.info(f"Successfully updated {driver_info['name']}")
                    save_path.unlink(missing_ok=True)
            else:
                self.logger.info(f"No updates available for device: {device_id}")

        def run(self):
            """Main execution method"""
            if not self.check_admin():
                self.logger.error("Admin privileges required")
                return

            self.logger.info("Starting driver update process")
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            device_ids = self.get_device_ids()
            if not device_ids:
                self.logger.info("No devices found requiring updates")
                return

            self.logger.info(f"Found {len(device_ids)} devices")

            with ThreadPoolExecutor(
                max_workers=self.config["concurrent_updates"]
            ) as executor:
                executor.map(self.process_device, device_ids)

            # Cleanup
            try:
                self.temp_dir.rmdir()
            except OSError:
                self.logger.warning("Could not remove temp directory - it may not be empty")

            self.logger.info("Driver update process completed")

        @staticmethod
        def check_admin():
            """Check for admin privileges"""
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except Exception:
                return False



    updater = DriverUpdater()
    if not updater.check_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return
    updater.run()


def check_platform_compatibility():
    supported = True
    warnings = []

    try:
        import tqdm
    except:
        supported = False
        warnings.append("Dependency 'tqdm' is missing")

    try:
        import requests
    except:
        supported = False
        warnings.append("Dependency 'requests' is missing")

    import platform
    if not platform.system() == "Windows":
        supported = False
        warnings.append("Platform not supported")

    return supported, warnings
