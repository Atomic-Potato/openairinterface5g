import socket

LISTEN_IP = "0.0.0.0"       # Listen on all available interfaces
LISTEN_PORT = 9999          # Matches the port in your C code hook

def main():
    # Set up the UDP server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    
    print(f"=== [PING TEST] Delay server is up and listening on UDP port {LISTEN_PORT} ===")
    print("Waiting for the CU to send a duplicated PDCP packet...")
    
    packet_count = 0
    try:
        while True:
            # Block until a packet arrives
            data, addr = server_socket.recvfrom(65535)
            packet_count += 1
            
            print(f"[{packet_count:04d}] SUCCESS! Received {len(data)} raw bytes from CU (IP: {addr[0]})")
            
    except KeyboardInterrupt:
        print("\nStopping the test server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()