import cv2, numpy as np, math, time, socket, struct, threading

# ============================
# Configuración UDP
# ============================
UDP_IP = "10.22.234.203"   # dirección del cliente
UDP_PORT = 5005        # mismo puerto que en Simulink

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Variables compartidas
_ref_angle_lock = threading.Lock()
_ref_angle_for_thread = 0.0  # radianes
send_period = 0.002  # 10 ms = 100 Hz
previous_angle = 0.0

# ============================
# Hilo de envío UDP
# ============================
def udp_sender_thread():
    global _ref_angle_for_thread
    while True:
        try:
            with _ref_angle_lock:
                value = _ref_angle_for_thread  # en radianes
            data = struct.pack('<d', value)  # double little-endian
            sock.sendto(data, (UDP_IP, UDP_PORT))
            time.sleep(send_period)
        except Exception as e:
            print("Error en envío UDP:", e)
            break

threading.Thread(target=udp_sender_thread, daemon=True).start()

# ============================
# Clase de Tracking
# ============================
class LiveAeroTracker:
    def __init__(self, cam_index=0, min_area_ratio=0.0005, alpha=0.1):
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.lower_yellow = np.array([20, 100, 100])
        self.upper_yellow = np.array([35, 255, 255])

        self.min_area_ratio = min_area_ratio
        self.alpha = alpha
        self.ema_ref = None
        self.ema_centroids = [None, None]
        self.fixed_ref = None

    def _smooth(self, old, new):
        if old is None: return new
        return (1 - self.alpha) * old + self.alpha * new

    def _find_two_largest(self, contours):
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return contours[:2] if len(contours) >= 2 else contours

    def _angle_conv(self, px, py, cx, cy):
        dx, dy = cx - px, cy - py
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90: ang -= 180
        elif ang < -90: ang += 180
        return math.radians(ang)

    def process_frame(self, frame):
        global _ref_angle_for_thread, previous_angle

        h, w = frame.shape[:2]
        min_area = max(1, int(self.min_area_ratio * w * h))

        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)

        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = [c for c in cnts if cv2.contourArea(c) >= min_area]
        cnts = self._find_two_largest(cnts)

        centroids = []
        for c in cnts:
            x, y, wc, hc = cv2.boundingRect(c)
            cx, cy = x + wc // 2, y + hc // 2
            centroids.append(np.array([cx, cy], dtype=np.float32))
            cv2.rectangle(frame, (x, y), (x + wc, y + hc), (0, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 8, (255, 0, 255), -1)

        if len(centroids) == 2:
            centroids.sort(key=lambda p: p[0])
            cL, cR = centroids
            self.ema_centroids[0] = self._smooth(self.ema_centroids[0], cL)
            self.ema_centroids[1] = self._smooth(self.ema_centroids[1], cR)
            cL, cR = self.ema_centroids

            ref = (cL + cR) / 2.0
            self.ema_ref = self._smooth(self.ema_ref, ref) if self.ema_ref is not None else ref
            ref = self.ema_ref

            if self.fixed_ref is None:
                self.fixed_ref = ref

            px, py = int(self.fixed_ref[0]), int(self.fixed_ref[1])
            angL = self._angle_conv(px, py, int(cL[0]), int(cL[1]))
            angR = self._angle_conv(px, py, int(cR[0]), int(cR[1]))
            avg_angle = (angL + angR) / 2.0

            # Suavizado en radianes
            smoothed_angle = 0.9 * previous_angle + 0.1 * avg_angle
            previous_angle = smoothed_angle

            with _ref_angle_lock:
                _ref_angle_for_thread = smoothed_angle

            # === VISUAL SUPPORT (en grados) ===
            cv2.line(frame, (int(cL[0]), int(cL[1])), (int(cR[0]), int(cR[1])), (0, 255, 0), 2)
            cv2.putText(frame, f"Angulo: {math.degrees(smoothed_angle):.1f} deg",
                        (px - 100, py - 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2, cv2.LINE_AA)

        return frame

    def release(self):
        if self.cap: self.cap.release()

# ============================
# Main
# ============================
def main():
    tracker = LiveAeroTracker(cam_index=0)
    print("Presiona 'q' para salir")

    while True:
        ok, frame = tracker.cap.read()
        if not ok:
            print("No se pudo leer el fotograma, usando último ángulo disponible...")
            time.sleep(0.01)
            continue

        annotated = tracker.process_frame(frame)
        cv2.imshow("Aero Live", annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    tracker.release()
    sock.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()