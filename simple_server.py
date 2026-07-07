import socket
import struct
import time

UDP_LISTEN_IP = "0.0.0.0"
UDP_LISTEN_PORT = 9999
PCAP_FILE = "pdcp_tap_capture.pcap"

# Redirect destination coordinates back to the CU process loop
CU_IP_ADDRESS = "192.168.71.150"  # Replace with your rfsim5g-oai-cu eth0 IP address
CU_INJECTION_PORT = 9998

PCAP_GLOBAL_HEADER = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 147)

print(f"Server mirroring traffic on port {UDP_LISTEN_PORT}...")
with open(PCAP_FILE, "wb") as pcap_file:
    pcap_file.write(PCAP_GLOBAL_HEADER)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            packet_len = len(data)
            
            # Log to PCAP
            now = time.time()
            pcap_file.write(struct.pack("<IIII", int(now), int((now - int(now)) * 1000000), packet_len, packet_len))
            pcap_file.write(data)
            pcap_file.flush()
            
            print(f"\n[MIRROR] Captured frame ({packet_len} bytes) leaving CU.")
            
            # Short transit delay to mimic a late-arriving radio reflection
            time.sleep(0.4)
            
            print(f"[RE-INJECT] Blasting duplicate back to CU engine at {CU_IP_ADDRESS}:{CU_INJECTION_PORT}")
            sock.sendto(data, (CU_IP_ADDRESS, CU_INJECTION_PORT))
            
    except KeyboardInterrupt:
        print("\nExiting server script.")