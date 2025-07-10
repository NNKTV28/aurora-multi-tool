name = "Application Performance Profiler"

def main():
    import psutil
    """Profile CPU and memory usage of running processes."""
    print("Application Performance Profiler")
    print("-" * 30)

    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        processes = sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)[
            :10
        ]  # Top 10 by CPU usage

        print(f"{'PID':<10}{'Name':<25}{'CPU%':<10}{'Memory (MB)':<15}")
        print("-" * 60)
        for proc in processes:
            print(
                f"{proc['pid']:<10}{proc['name']:<25}{proc['cpu_percent']:<10.2f}"
                f"{proc['memory_info'].rss / (1024 * 1024):<15.2f}"
            )
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
