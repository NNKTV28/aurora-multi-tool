import python_nmap as nmap  # type: ignore


def port_scanner():
    """Scan open ports on a target host."""
    print("Port Scanner")
    print("-" * 30)

    try:
        target = input("Enter the target IP or hostname: ").strip()
        ports = input("Enter the range of ports to scan (e.g., 1-1000): ").strip()

        scanner = nmap.PortScanner()
        print(f"\nScanning {target} on ports {ports}...")
        scanner.scan(hosts=target, ports=ports)

        for host in scanner.all_hosts():
            print(f"\nHost: {host} ({scanner[host].hostname()})")
            print(f"State: {scanner[host].state()}")
            for proto in scanner[host].all_protocols():
                print(f"\nProtocol: {proto}")
                ports = scanner[host][proto].keys()
                for port in sorted(ports):
                    print(f"Port: {port}, State: {scanner[host][proto][port]['state']}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    port_scanner()


if __name__ == "__main__":
    main()
