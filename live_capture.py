from scapy.all import sniff, IP, IPv6
import pandas as pd
from collections import defaultdict


def capture_live(duration=5):

    # Store traffic per IP
    traffic = defaultdict(lambda: {"Requests": 0, "Data_Size": 0})

    def process(packet):

        # Check IPv4
        if packet.haslayer(IP):
            ip = packet[IP].src

        # Check IPv6
        elif packet.haslayer(IPv6):
            ip = packet[IPv6].src

        else:
            return

        # Update stats
        traffic[ip]["Requests"] += 1
        traffic[ip]["Data_Size"] += len(packet)

    # Capture packets
    sniff(prn=process, timeout=duration)

    # Convert to list
    data = []
    for ip, stats in traffic.items():
        data.append({
            "IP_Address": ip,
            "Requests": stats["Requests"],
            "Data_Size": stats["Data_Size"]
        })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Handle empty case
    if df.empty:
        return pd.DataFrame(columns=["IP_Address", "Requests", "Data_Size"])

    return df