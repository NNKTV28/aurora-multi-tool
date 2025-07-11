name = "System Information"

def main():
    import platform
    import psutil
    from datetime import datetime
    import json
    from pathlib import Path
    import wmi
    import logging
    from typing import Dict, Any


    class SystemInfoCollector:
        def __init__(self):
            self.setup_logging()
            self.wmi = wmi.WMI()

        def setup_logging(self):
            """Configure logging system"""
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = (
                log_dir / f'system_info_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            )
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
            )
            self.logger = logging.getLogger(__name__)

        def get_system_info(self) -> Dict[str, Any]:
            """Collect system information"""
            try:
                info = {
                    "System": self._get_os_info(),
                    "CPU": self._get_cpu_info(),
                    "Memory": self._get_memory_info(),
                    "Disk": self._get_disk_info(),
                    "Network": self._get_network_info(),
                    "Graphics": self._get_graphics_info(),
                }
                return info
            except Exception as e:
                self.logger.error(f"Error collecting system information: {e}")
                return {}

        def _get_os_info(self) -> Dict[str, str]:
            """Get operating system information"""
            return {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "OS Release": platform.release(),
                "Architecture": platform.machine(),
                "Computer Name": platform.node(),
            }

        def _get_cpu_info(self) -> Dict[str, Any]:
            """Get CPU information"""
            cpu_info = {
                "Physical Cores": psutil.cpu_count(logical=False),
                "Total Cores": psutil.cpu_count(logical=True),
                "CPU Usage": f"{psutil.cpu_percent()}%",
            }

            # Get detailed CPU info from WMI
            for cpu in self.wmi.Win32_Processor():
                cpu_info.update(
                    {
                        "Processor": cpu.Name,
                        "Base Speed": f"{cpu.MaxClockSpeed} MHz",
                        "Architecture": cpu.Architecture,
                    }
                )

            return cpu_info

        def _get_memory_info(self) -> Dict[str, str]:
            """Get memory information"""
            memory = psutil.virtual_memory()
            return {
                "Total": f"{memory.total / (1024**3):.2f} GB",
                "Available": f"{memory.available / (1024**3):.2f} GB",
                "Used": f"{memory.used / (1024**3):.2f} GB",
                "Percentage": f"{memory.percent}%",
            }

        def _get_disk_info(self) -> Dict[str, Dict[str, str]]:
            """Get disk information"""
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        "Mount Point": partition.mountpoint,
                        "File System": partition.fstype,
                        "Total": f"{usage.total / (1024**3):.2f} GB",
                        "Used": f"{usage.used / (1024**3):.2f} GB",
                        "Free": f"{usage.free / (1024**3):.2f} GB",
                        "Percentage": f"{usage.percent}%",
                    }
                except Exception as e:
                    self.logger.warning(
                        f"Error getting disk info for {partition.device}: {e}"
                    )
            return disks

        def _get_network_info(self) -> Dict[str, Dict[str, str]]:
            """Get network interfaces information"""
            interfaces = {}
            for name, stats in psutil.net_if_stats().items():
                try:
                    interfaces[name] = {
                        "Status": "Up" if stats.isup else "Down",
                        "Speed": f"{stats.speed} Mbps" if stats.speed else "Unknown",
                        "MTU": str(stats.mtu),
                    }
                except Exception as e:
                    self.logger.warning(f"Error getting network info for {name}: {e}")
            return interfaces

        def _get_graphics_info(self) -> Dict[str, str]:
            """Get graphics card information"""
            graphics_info = {}
            try:
                for gpu in self.wmi.Win32_VideoController():
                    graphics_info[gpu.Name] = {
                        "Driver Version": gpu.DriverVersion,
                        "Video Memory": f"{int(gpu.AdapterRAM) / (1024**3):.2f} GB"
                        if gpu.AdapterRAM
                        else "Unknown",
                        "Video Processor": gpu.VideoProcessor,
                        "Resolution": (
                            f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}"
                        ),
                    }
            except Exception as e:
                self.logger.warning(f"Error getting graphics info: {e}")
            return graphics_info

        def save_report(self, info: Dict[str, Any], filename: str = "system_report.json"):
            """Save system information to a file"""
            try:
                reports_dir = Path("reports")
                reports_dir.mkdir(exist_ok=True)

                report_path = reports_dir / filename
                with open(report_path, "w") as f:
                    json.dump(info, f, indent=4)

                self.logger.info(f"System report saved to {report_path}")
                return True
            except Exception as e:
                self.logger.error(f"Error saving system report: {e}")
                return False

        def display_info(self, info: Dict[str, Any]):
            """Display system information in a formatted way"""
            print("\nSystem Information Report")
            print("=" * 50)

            for section, data in info.items():
                print(f"\n{section}:")
                print("-" * 30)

                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"\n{key}:")
                            for subkey, subvalue in value.items():
                                print(f"  {subkey}: {subvalue}")
                        else:
                            print(f"{key}: {value}")
                else:
                    print(data)



    collector = SystemInfoCollector()

    print("\nCollecting system information...")
    system_info = collector.get_system_info()

    if not system_info:
        print("Error collecting system information.")
        return

    collector.display_info(system_info)

    save = input("\nWould you like to save this report? (y/n): ").lower().strip()
    if save == "y":
        filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if collector.save_report(system_info, filename):
            print("\nReport saved successfully!")
        else:
            print("\nError saving report.")

    input("\nPress Enter to continue...")


def check_platform_compatibility():
    supported = True
    warnings = []

    try:
        import psutil
    except:
        supported = False
        warnings.append("Dependency 'psutil' is missing")

    try:
        import wmi
    except:
        supported = False
        warnings.append("Dependency 'wmi' is missing")

    import platform
    if not platform.system() == "Windows":
        supported = False
        warnings.append("Platform not supported")

    return supported, warnings
