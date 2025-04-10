import psutil
import time


def disk_speed_test():
    """Perform a disk speed test by measuring read/write speeds."""
    print("Disk Speed Test")
    print("-" * 30)

    try:
        disk_io_start = psutil.disk_io_counters()
        time.sleep(1)  # Measure over 1 second
        disk_io_end = psutil.disk_io_counters()

        read_speed = (disk_io_end.read_bytes - disk_io_start.read_bytes) / (
            1024 * 1024
        )  # MB/s
        write_speed = (disk_io_end.write_bytes - disk_io_start.write_bytes) / (
            1024 * 1024
        )  # MB/s

        print(f"Read Speed: {read_speed:.2f} MB/s")
        print(f"Write Speed: {write_speed:.2f} MB/s")
    except Exception as e:
        print(f"Error: {e}")


def main():
    disk_speed_test()


if __name__ == "__main__":
    main()
