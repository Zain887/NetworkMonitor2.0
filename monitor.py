from network_utils import ping, check_sip_ports
from config import MAIN_PBX_IP

def check_device(device):

    ip = str(device.get("IP Address", "")).strip()

    if not ip:
        return None

    name = device.get("Device Name", "Unknown")
    phone = device.get("Contact Number", "")
    dtype = str(device.get("Device Type", "CAMERA")).upper()

    online = ping(ip)

    status = "ONLINE" if online else "OFFLINE"

    if online and dtype == "VOIP" and ip != MAIN_PBX_IP:

        sip_ok = check_sip_ports(ip)

        if not sip_ok:
            online = False
            status = "SIP REGISTRATION FAILED"

    return {
        "name": name,
        "ip": ip,
        "phone": phone,
        "type": dtype,
        "online": online,
        "status": status
    }