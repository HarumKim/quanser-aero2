## 🎥 Visual Control Mini-Projects — Quanser Aero 2

This repository contains a sequence of three mini-projects developed as part of the course MR3003C – Autonomía de Vehículos Aéreos No Tripulados, focused on vision-based control of the Quanser Aero 2 platform.

The projects are structured as incremental challenges, evolving from offline visual analysis to real-time visual servoing across multiple devices.

---

### 🧪 Project Overview

The three assignments explore how computer vision can be used to extract orientation information from the Quanser Aero 2 and use it as feedback for control systems, progressively increasing realism and system complexity.

---

### 🟢 HW1 — Vision-Based Angle Estimation & Simulated Control
**Goal:**   
Control the orientation of the Quanser Aero 2 using only two images: an initial position and a target position.

**What it does:**
- Detects yellow rotor markers using image processing.

- Computes initial and final rotor angles relative to a reference axis.

- Uses the extracted angles as input to a PID controller.

- Simulates the system dynamics using a simplified second-order model in Python.

**Key ideas:**
- Vision-based angle estimation

- PID control fundamentals

- Offline simulation of drone dynamics

**Outcome:**  
A proportional controller was sufficient to drive the system to the desired orientation in simulation, validating the vision-to-control pipeline.

<img width="1519" height="655" alt="image" src="https://github.com/user-attachments/assets/a6dcf79d-cd6f-43d0-a92f-170c69229f8a" />

### 🟡 HW2 — Real-Time Vision Control of a Simulated Aero 2

**Goal:**   
Control a digital twin of the Quanser Aero 2 in Simulink using real-time visual feedback from a camera.

**What it does:**    
- Tracks yellow rotor markers from a live camera or video using OpenCV.

- Computes rotor angles in real time.

- Sends angle data via UDP communication to Simulink.

- Simulink applies a PID controller to the Aero 2 simulation using QUARC.

**System architecture:**  
- Python: vision processing + angle extraction

- UDP: real-time communication

- Simulink + QUARC: control and simulation

**Outcome:**    
The simulated Aero 2 successfully follows the orientation observed by the camera, demonstrating closed-loop visual control with networked communication.

### 🎥 Video Demonstration

[![HW2 – Real-Time Vision Control Demo](https://github.com/user-attachments/assets/abcd1234-5678)](https://drive.google.com/file/d/1FWcYRiCcNFb9V74LbIeGihvQPLKtQtmz/view)


### 🔴 HW3 — Real-Time Visual Control Between Two Aero 2 Systems

**Goal:**    
Achieve real-time visual servoing, where one physical Aero 2 controls another Aero 2 through vision.

**What it does:**
- A camera observes a real Aero 2 and tracks rotor angles live.

- Angles are transmitted via UDP to a second system.

- The receiving system feeds the data into Simulink.

- Simulink controls another Aero 2 to match the observed motion.

**Key challenges addressed:**
- Multi-device communication

- Network latency and delay

- Signal saturation and stability

- Real-time vision-to-control integration

Outcome:  
The system successfully mirrors the motion of one Aero 2 onto another using visual feedback, completing the transition from simulation to real-time visual control.
