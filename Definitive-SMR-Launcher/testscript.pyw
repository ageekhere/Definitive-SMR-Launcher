import socket
import re
import time
import threading

# --- CONFIGURATION ---
TARGET_IP = '134.122.16.249'
PORT = 27900
GAME = "smrailroads"
KEY = "092Zbc"

def gsseckey(secure, key):
    """The GameSpy encryption algorithm to solve the \secure\ challenge."""
    buff = list(range(256))
    secbuf = list(key.encode('ascii')) + [0]
    edx = k = 0
    for i in range(256):
        if secbuf[k] == 0: k = 0
        edx = (buff[i] + edx + secbuf[k]) % 256
        buff[i], buff[edx] = buff[edx], buff[i]
        k += 1
    secbuf = list(secure.encode('ascii')) + [0]
    edi = ebx = 0
    for i in range(6):
        edi = (edi + secbuf[i] + 1) % 256
        ebx = (ebx + buff[edi]) % 256
        buff[edi], buff[ebx] = buff[ebx], buff[edi]
        ecx = (buff[edi] + buff[ebx]) % 256
        secbuf[i] ^= buff[ecx]
    for i in range(6): secbuf[i] ^= ord(key[i]) 
    def gsval(r):
        if r < 26: return chr(r + 65)
        if r < 52: return chr(r + 71)
        if r < 62: return chr(r - 4)
        return '+' if r == 62 else '/'
    v = []
    for i in range(2):
        t1, t2, t3 = secbuf[3*i], secbuf[3*i+1], secbuf[3*i+2]
        v.append(gsval(t1 >> 2)); v.append(gsval(((t1 & 3) << 4) | (t2 >> 4)))
        v.append(gsval(((t2 & 0xf) << 2) | (t3 >> 6))); v.append(gsval(t3 & 0x3f))
    return ''.join(v)

def player_thread(name, game_port):
    """Simulates a single player hosting a game."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    hb = f"\\heartbeat\\{game_port}\\gamename\\{GAME}\\hostname\\{name}\\public\\1\\state\\1\\final\\"
    
    print(f"[*] [{name}] Sending heartbeat...")
    
    while True:
        try:
            # Send Heartbeat
            sock.sendto(hb.encode(), (TARGET_IP, PORT))
            
            # Wait for Challenge
            data, addr = sock.recvfrom(1024)
            resp = data.decode('ascii', errors='ignore')
            
            if "\\secure\\" in resp:
                challenge = re.search(r'\\secure\\([^\\]+)', resp).group(1)
                response = gsseckey(challenge, KEY)
                
                # Send Validation
                valid_packet = f"\\validate\\{response}\\final\\"
                sock.sendto(valid_packet.encode(), (TARGET_IP, PORT))
                print(f"[+] [{name}] Validated and Active.")
            
            # Keep-alive sleep
            time.sleep(30)
            
        except socket.timeout:
            # If we timeout, just try again (server might be busy)
            continue
        except Exception as e:
            print(f"[-] [{name}] Error: {e}")
            break

def run_test():
    print("="*50)
    print("RAILROADS! DOUBLE-GHOST HANDSHAKE TEST")
    print("="*50)
    
    # Start two virtual players on different threads
    t1 = threading.Thread(target=player_thread, args=("Alpha_Ghost", 2626), daemon=True)
    t2 = threading.Thread(target=player_thread, args=("Beta_Ghost", 2627), daemon=True)
    
    t1.start()
    t2.start()
    
    print("[!] Both players are now heartbeating.")
    print("[!] Keep this running and check your Lobby Monitor script.")
    print("-" * 50)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

if __name__ == "__main__":
    run_test()