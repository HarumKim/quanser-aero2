import socket
import struct
import time
import threading

# ============================
# Configuración
# ============================

# IP y puerto del tracker (emisor UDP)
TRACKER_IP = "0.0.0.0"  # IP de la máquina que envía los ángulos
TRACKER_PORT = 5005            # Puerto del tracker

# IP y puerto de Simulink (receptor UDP)
SIMULINK_IP = "127.0.0.1"  # IP de la máquina con Simulink
SIMULINK_PORT = 5006            # Puerto en Simulink

# ============================
# Socket UDP para recibir del tracker
# ============================
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", TRACKER_PORT))
print(f"Escuchando UDP del tracker en 0.0.0.0:{TRACKER_PORT}...")

# ============================
# Socket UDP para enviar a Simulink
# ============================
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ============================
# Función principal
# ============================
def forward_angles():
    try:
        while True:
            data, addr = recv_sock.recvfrom(1024)  # recibe datagramas
            if data:
                angle = struct.unpack('<d', data[:8])[0]
                print(f"Ángulo recibido de {addr}: {angle:.4f} rad ({angle*180/3.1416:.2f}°)")

                # Reenvía a Simulink
                send_sock.sendto(data, (SIMULINK_IP, SIMULINK_PORT))

            time.sleep(0.002)

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")

    finally:
        recv_sock.close()
        send_sock.close()
        print("Sockets cerrados.")

# ============================
# Inicia el reenvío
# ============================
if __name__ == "__main__":
    forward_angles()
