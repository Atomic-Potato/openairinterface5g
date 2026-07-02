import socket
import struct
import time

UDP_LISTEN_IP = "0.0.0.0"
UDP_LISTEN_PORT = 9999
CU_RX_PORT = 9998  # The port our modified CU will listen on
PCAP_FILE = "pdcp_tap_capture.pcap"

# TODO: Replace these with your target UE's networking coordinates!
UE_IP_ADDRESS = "192.168.71.181"  # Target UE stack IP address
UE_PDCP_PORT = 4043             # The port where the UE stack receives incoming radio packets

# --- PCAP Global Header Template ---
# Magic number, Version major, Version minor, Thiszone, Sigfigs, Snaplen, Network (147 = LINKTYPE_USER0)
PCAP_GLOBAL_HEADER = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 147)

print(f"PDCP Tap & Injector Server listening on UDP port {UDP_LISTEN_PORT}...")
print(f"Writing live traffic to: {PCAP_FILE}")

# Open the file and initialize the PCAP layout
with open(PCAP_FILE, "wb") as pcap_file:
    pcap_file.write(PCAP_GLOBAL_HEADER)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))

    try:
        while True:
            # 1. Capture the PDU going out from the CU
            data, addr = sock.recvfrom(4096)
            packet_len = len(data)
            
            # 2. Log original packet out to PCAP for inspection
            now = time.time()
            ts_sec = int(now)
            ts_usec = int((now - ts_sec) * 1000000)
            pcap_packet_header = struct.pack("<IIII", ts_sec, ts_usec, packet_len, packet_len)
            pcap_file.write(pcap_packet_header)
            pcap_file.write(data)
            pcap_file.flush()
            
            print(f"\n[TAP] Captured {packet_len} bytes from CU.")
            
            # 3. Apply a short delay (e.g., 400 milliseconds)
            # This ensures the standard CU -> DU -> UE packet finishes its transit journey first
            delay_seconds = 0.4
            print(f"[DELAY] Holding duplicate packet for {delay_seconds} seconds...")
            time.sleep(delay_seconds)
            
            # 4. Inject directly to the UE's lower layer protocol entrypoint
            print(f"[DUPLICATE] Blasting packet straight to UE at {UE_IP_ADDRESS}:{UE_PDCP_PORT}")
            sock.sendto(data, (UE_IP_ADDRESS, UE_PDCP_PORT))
            
    except KeyboardInterrupt:
        print("\nStopping integrated server cleanly.")