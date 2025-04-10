import speedtest


def network_speed_test():
    """Perform a network speed test."""
    print("Network Speed Test")
    print("-" * 30)

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / (1024 * 1024)  # Convert to Mbps
        upload_speed = st.upload() / (1024 * 1024)  # Convert to Mbps

        print(f"Download Speed: {download_speed:.2f} Mbps")
        print(f"Upload Speed: {upload_speed:.2f} Mbps")
    except Exception as e:
        print(f"Error: {e}")


def main():
    network_speed_test()


if __name__ == "__main__":
    main()
