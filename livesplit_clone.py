import tkinter as tk
from tkinter import ttk
import json
import time
import os

# --------------------
# Config
# --------------------
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "keys": {
        "start": "<space>",
        "reset": "r",
        "save": "s",
        "toggle_ui": "u",
        "fullscreen": "f",
        "invert_colors": "i",
        "hotkey_settings": "h"
    },
    "ui": {
        "bg_color": "#111111",
        "opacity": 0.95
    }
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

KEYS = CONFIG["keys"]
UI = CONFIG["ui"]

# --------------------
# Timer state
# --------------------
running = False
start_time = 0.0
elapsed = 0.0
splits = []
ui_visible = False
invert_colors = False
fullscreen = False
sound_played = False
hotkey_window_ref = None

# --------------------
# Volume control
# --------------------
volume = 1.0
prev_volume = volume
volume_ui_visible = False

def set_volume(val):
    global volume
    volume = float(val)

def toggle_volume_ui():
    global volume_ui_visible
    if volume_ui_visible:
        volume_frame.pack_forget()
        volume_ui_visible = False
    else:
        volume_frame.pack(side="top", pady=5)
        volume_ui_visible = True

def apply_volume():
    global prev_volume
    prev_volume = volume
    toggle_volume_ui()

def revert_volume():
    global volume
    volume = prev_volume
    volume_slider.set(volume)
    toggle_volume_ui()

# --------------------
# Hotkey Settings
# --------------------
def open_hotkey_window():
    global hotkey_window_ref
    if hotkey_window_ref is not None and hotkey_window_ref.winfo_exists():
        hotkey_window_ref.destroy()
        hotkey_window_ref = None
        return

    hotkey_window_ref = tk.Toplevel(root)
    hotkey_window_ref.title("Hotkey Settings")
    hotkey_window_ref.configure(bg="#222222")
    hotkey_window_ref.geometry("300x300")
    entries = {}

    def save_hotkeys():
        global hotkey_window_ref
        for key_name, entry in entries.items():
            KEYS[key_name] = entry.get()
        with open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG, f, indent=4)
        hotkey_window_ref.destroy()
        hotkey_window_ref = None

    def revert_hotkeys():
        global hotkey_window_ref
        hotkey_window_ref.destroy()
        hotkey_window_ref = None

    row = 0
    for k in KEYS:
        tk.Label(hotkey_window_ref, text=k, bg="#222222", fg="#fff").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry = tk.Entry(hotkey_window_ref)
        entry.insert(0, KEYS[k])
        entry.grid(row=row, column=1, padx=5, pady=5)
        entries[k] = entry
        row += 1

    tk.Button(hotkey_window_ref, text="Apply", bg="#00ff88", fg="#000000", relief="raised", bd=2, command=save_hotkeys).grid(row=row, column=0, pady=10)
    tk.Button(hotkey_window_ref, text="Revert", bg="#888888", fg="#000000", relief="raised", bd=2, command=revert_hotkeys).grid(row=row, column=1, pady=10)

# --------------------
# Helper functions
# --------------------
def lerp_color(color1, color2, t):
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_split_colors(value, first_value, max_diff):
    if len(splits) == 1:
        return "#ffff00", "#444400"
    if max_diff == 0:
        return "#0000ff", "#004400"
    ratio = min(max((value - first_value) / max_diff, 0), 1)
    if invert_colors:
        fg = lerp_color((255,0,0), (0,0,255), ratio)
        bg = lerp_color((64,0,0), (0,64,0), ratio)
    else:
        fg = lerp_color((0,0,255), (255,0,0), ratio)
        bg = lerp_color((0,64,0), (64,0,0), ratio)
    return fg, bg

def gradient_text(t, start=(200,200,200), end=(255,255,255)):
    return lerp_color(start, end, t)

def gradient_green_text(t):
    start = (100, 255, 150)
    end   = (0, 255, 128)
    return lerp_color(start, end, t)

def play_beep():
    try:
        os.system(f'play -nq -t alsa synth 0.3 sine 1200 vol {volume}')
    except:
        pass

# --------------------
# Timer logic
# --------------------
def toggle_timer(event=None):
    global running, start_time, elapsed, sound_played
    if not running:
        start_time = time.time() - elapsed
        running = True
        sound_played = False
    else:
        elapsed = time.time() - start_time
        running = False

def reset_timer(event=None):
    global running, elapsed
    running = False
    elapsed = 0.0
    timer_label.config(text="0.00s", fg=gradient_text(0))

def save_split(event=None):
    current = elapsed if not running else time.time() - start_time
    splits.append(current)
    update_split_list()

def remove_split(index):
    splits.pop(index)
    update_split_list()

# --------------------
# UI functions
# --------------------
def update_split_list():
    for widget in split_canvas.winfo_children():
        widget.destroy()
    if not splits:
        return
    first_value = splits[0]
    max_diff = max(splits) - first_value if len(splits) > 1 else 0
    for i, val in enumerate(splits):
        fg, bg = get_split_colors(val, first_value, max_diff)
        frame = tk.Frame(split_canvas, bg=bg)
        frame.pack(fill="x", pady=1, padx=2)
        label = tk.Label(frame, text=f"{i+1} → {val:.2f}s", fg=fg, bg=bg,
                         font=("Arial", 12, "bold"))
        label.pack(side="left", padx=5, pady=2)
        btn = tk.Button(frame, text="X", command=lambda idx=i: remove_split(idx),
                        bg="#333333", fg="#ffffff", width=2, relief="flat")
        btn.pack(side="right", padx=5)

def toggle_ui(event=None):
    global ui_visible
    ui_visible = not ui_visible
    if ui_visible:
        control_frame.pack(fill="x", pady=6)
        toggle_btn.config(text="<")
    else:
        control_frame.pack_forget()
        toggle_btn.config(text=">")

def toggle_invert(event=None):
    global invert_colors
    invert_colors = not invert_colors
    update_split_list()

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        split_list_frame.pack_forget()
        control_frame.pack_forget()
        toggle_btn.pack_forget()
        invert_btn.place_forget()
        volume_btn.place_forget()
        hotkey_btn.place_forget()
    else:
        split_list_frame.pack(fill="both", expand=True, padx=8, pady=6)
        if ui_visible:
            control_frame.pack(fill="x", pady=6)
        toggle_btn.pack()
        invert_btn.place(x=5, y=5)
        volume_btn.place(x=45, y=5)
        hotkey_btn.place(x=85, y=5)

# --------------------
# Timer loop
# --------------------
def update_timer():
    global elapsed, sound_played
    if running:
        elapsed = time.time() - start_time
        fraction = (elapsed % 1)
        timer_label.config(text=f"{elapsed:.2f}s", fg=gradient_green_text(fraction))
        if splits and elapsed > max(splits) and not sound_played:
            play_beep()
            sound_played = True
    else:
        fraction = (elapsed % 1)
        timer_label.config(fg=gradient_text(fraction))
    root.after(10, update_timer)

# --------------------
# Window setup
# --------------------
root = tk.Tk()
root.title("Speedrun Timer")
root.geometry("340x480")
root.configure(bg=UI["bg_color"])
root.attributes("-alpha", UI["opacity"])

# Timer label
timer_label = tk.Label(root, text="0.00s", font=("Arial", 36, "bold"),
                       fg=gradient_text(0), bg=UI["bg_color"])
timer_label.pack(pady=10)

# Top-left invert button
invert_btn = tk.Button(root, text="🔄", width=3, command=toggle_invert,
                       bg="#444444", fg="#ffffff", relief="raised", bd=2)
invert_btn.place(x=5, y=5)

# Top-left volume button
volume_btn = tk.Button(root, text="🔊", width=3, command=toggle_volume_ui,
                       bg="#444444", fg="#ffffff", relief="raised", bd=2)
volume_btn.place(x=45, y=5)

# Hotkey settings button
hotkey_btn = tk.Button(root, text="⌨️", width=3, command=open_hotkey_window,
                       bg="#444444", fg="#ffffff", relief="raised", bd=2)
hotkey_btn.place(x=85, y=5)

# Toggle button for manual controls
toggle_btn = tk.Button(root, text=">", width=2, command=toggle_ui,
                       bg="#444444", fg="#ffffff", relief="raised", bd=2)
toggle_btn.pack()

# Manual control buttons frame
control_frame = tk.Frame(root, bg="#222222")
tk.Button(control_frame, text="Start / Stop", command=toggle_timer,
          bg="#333333", fg="#ffffff", relief="raised", bd=2).pack(pady=2, fill="x")
tk.Button(control_frame, text="Save Split", command=save_split,
          bg="#333333", fg="#ffffff", relief="raised", bd=2).pack(pady=2, fill="x")
tk.Button(control_frame, text="Reset Timer", command=reset_timer,
          bg="#333333", fg="#ffffff", relief="raised", bd=2).pack(pady=2, fill="x")

# Frame with scrollbar for splits
split_list_frame = tk.Frame(root, bg="#222222")
split_list_frame.pack(fill="both", expand=True, padx=8, pady=6)
split_canvas = tk.Frame(split_list_frame, bg="#222222")
split_canvas.pack(fill="both", expand=True)
scrollbar = ttk.Scrollbar(split_list_frame, orient="vertical", command=lambda *args: split_canvas.yview(*args))
scrollbar.pack(side="right", fill="y")

# Volume frame
volume_frame = tk.Frame(root, bg="#555555")
volume_slider = tk.Scale(volume_frame, from_=0, to=1.0, resolution=0.01, orient="horizontal",
                         bg="#aaaaaa", fg="#000000", troughcolor="#888888", length=150,
                         command=lambda val: set_volume(float(val)))
volume_slider.set(volume)
volume_slider.pack(side="left", padx=5, pady=2)

done_btn = tk.Button(volume_frame, text="Done", bg="#00ff88", fg="#000000", relief="raised", bd=2,
                     command=apply_volume)
done_btn.pack(side="left", padx=5)

revert_btn = tk.Button(volume_frame, text="Revert", bg="#888888", fg="#000000", relief="raised", bd=2,
                       command=revert_volume)
revert_btn.pack(side="left", padx=5)

# --------------------
# Key bindings
# --------------------
root.bind(KEYS["start"], toggle_timer)
root.bind(KEYS["reset"], reset_timer)
root.bind(KEYS["save"], save_split)
root.bind(KEYS["toggle_ui"], toggle_ui)
root.bind(KEYS["fullscreen"], toggle_fullscreen)
root.bind(KEYS["hotkey_settings"], lambda e=None: open_hotkey_window())
root.bind(KEYS["invert_colors"], toggle_invert)

# --------------------
update_timer()
root.mainloop()
