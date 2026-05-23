import platform
import socket
import subprocess

def ping(ip):
    """
    Executes an ICMP echo verification check against the targeted interface.
    """
    is_windows = platform.system().lower() == "windows"
    cmd = (
        ["ping", "-n", "1", "-w", "1000", str(ip)] 
        if is_windows 
        else ["ping", "-c", "1", "-W", "1", str(ip)]
    )
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def check_sip_ports(ip, ports=[5060, 5927], timeout=2):
    """
    Attempts a raw network socket handshake over the specified SIP signaling ports.
    """
    for port in ports:
        try:
            # Reverted to match your exact single-file working socket connection logic
            with socket.create_connection((str(ip), port), timeout=timeout):
                return True  
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue  
    return False