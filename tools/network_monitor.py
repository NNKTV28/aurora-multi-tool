name = "Network Monitor"

def main():
    import psutil
    import time

    """Monitor network activity."""
    print("Network Monitor")
    print("-" * 30)

    try:
        print("Press Ctrl+C to stop monitoring.\n")
        while True:
            net_io = psutil.net_io_counters()
            upload_speed = net_io.bytes_sent / (1024 * 1024)  # Convert to MB
            download_speed = net_io.bytes_recv / (1024 * 1024)  # Convert to MB

            print(
                f"Upload: {upload_speed:.2f} MB | Download: {download_speed:.2f} MB",
                end="\r",
            )
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")

def check_platform_compatibility():
    supported = True
    warnings = []

    try:
        import psutil
    except:
        supported = False
        warnings.append("Dependency 'psutil' is missing")

    return supported, warnings
