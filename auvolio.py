#!/usr/bin/env python3
import subprocess
import socketio

# =========================
# CONFIGURATION
# =========================
SINK = "0"  # ganti sesuai sink USB sound card
SERVER_URL = "http://192.168.1.52:3000"  # IP server M1

# =========================
# FUNCTIONS
# =========================
def set_volume(percent):
    subprocess.run(["pactl", "set-sink-volume", SINK, f"{percent}%"])

def change_volume(delta):
    if delta >= 0:
        subprocess.run(["pactl", "set-sink-volume", SINK, f"+{delta}%"])
    else:
        subprocess.run(["pactl", "set-sink-volume", SINK, f"{delta}%"])

def toggle_mute():
    subprocess.run(["pactl", "set-sink-mute", SINK, "toggle"])

def get_volume():
    result = subprocess.run(
        ["pactl", "get-sink-volume", SINK],
        capture_output=True, text=True
    )
    lines = result.stdout.splitlines()
    if not lines:
        return "Unknown (no output)"
    line = lines[0]
    try:
        percent = line.split("/")[1].strip()
        return percent
    except IndexError:
        return "Unknown"


# =========================
# SOCKET.IO CLIENT
# =========================
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server!")

@sio.event
def disconnect():
    print("Disconnected from server!")

@sio.on("set_volume")
def on_set_volume(data):
    print("Received volume command:", data)

    # Tentukan tipe data
    if isinstance(data, dict):
        vol = data.get("volume")
    else:
        vol = data  # bisa int atau string langsung

    # Handle volume
    if vol == "mute":
        toggle_mute()
    elif isinstance(vol, str) and (vol.startswith("+") or vol.startswith("-")):
        try:
            delta = int(vol)
            change_volume(delta)
        except ValueError:
            print("Invalid delta volume:", vol)
    else:
        try:
            percent = int(vol)
            if 0 <= percent <= 100:
                set_volume(percent)
            else:
                print("Volume out of range (0-100)")
        except ValueError:
            print("Invalid volume:", vol)

    print("Current volume:", get_volume())

# =========================
# CONNECT TO SERVER
# =========================
if __name__ == "__main__":
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except KeyboardInterrupt:
        print("Exiting...")