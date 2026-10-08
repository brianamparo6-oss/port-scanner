import re
import socket
import ipaddress
from common_ports import ports_and_services


def get_open_ports(target, port_range, verbose=False):
    open_ports = []

    # A target made only of digits and dots is treated as an IP address
    looks_like_ip = re.fullmatch(r"[\d.]+", target) is not None

    if looks_like_ip:
        try:
            ip = str(ipaddress.ip_address(target))
        except ValueError:
            return "Error: Invalid IP address"
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except OSError:
            hostname = None
    else:
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return "Error: Invalid hostname"
        hostname = target

    # Scan every port in the range, including both ends
    for port in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
        except OSError:
            pass
        finally:
            s.close()

    if not verbose:
        return open_ports

    if hostname:
        header = f"Open ports for {hostname} ({ip})"
    else:
        header = f"Open ports for {ip}"

    lines = [header, "PORT     SERVICE"]
    for port in open_ports:
        service = ports_and_services.get(port, "unknown")
        lines.append(f"{port:<9}{service}")
    return "\n".join(lines)
