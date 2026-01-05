import tkinter as tk
import time
import json

# --------------------
# Load config
# --------------------
with open("config.json", "r") as f:
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

ui_visible = False  # manual buttons hidden at start

# --------------------
# Helper functions
# --------------------
def lerp_color(color1, color2, t):
    """Linear interpolation between two RGB colors, t in [0,1]"""
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_split_colors(value, first_value, max_diff):
    """Return (fg_color, bg_color) for a split based on its delta"""
    if max_diff == 0:
        return "#0000ff", "#004400"  # single split: blue text, dark green bg
    ratio = min(max((value - first_value) / max_diff, 0), 1)
    fg = lerp_color((0,0,255), (255,0,0), ratio)       # blue → red
    bg = lerp_color((0,64,0), (64,0,0), ratio)         # green → dark red
    return fg, bg

# --------------------
# Timer logic
# --------------------
def toggle_timer(event=None):
    global running, start_time, elapsed
    if not running:
        start_time = time.time() - elapsed
        running = True
    else:
        elapsed = time.time() - start_time
        running = False

def reset_timer(event=None):
    """Reset only current timer, not splits"""
    global running, elapsed
    running = False
    elapsed = 0.0
    timer_label.config(text="0.00s", fg="#ffffff")

def save_split(event=None):
    """Save current timer as a split"""
    current = elapsed if not running else time.time() - start_time
    splits.append(current)
    update_split_list()

def remove_split(index):
    """Remove a split by index"""
    splits.pop(index)
    update_split_list()

# --------------------
# Update split list UI
# --------------------
def update_split_list():
    """Re-render all split rows with proper colors and background gradient"""
    for widget in split_list_frame.winfo_children():
        widget.destroy()

    if not splits:
        return

    first_value = splits[0]
    max_diff = max(splits) - first_value if len(splits) > 1 else 0

    for i, val in enumerate(splits):
        fg, bg = get_split_colors(val, first_value, max_diff)
        frame = tk.Frame(split_list_frame, bg=bg)
        frame.pack(fill="x", pady=1)

        label = tk.Label(frame, text=f"{i+1} → {val:.2f}s", fg=fg, bg=bg)
        label.pack(side="left", padx=5)

        btn = tk.Button(frame, text="X", command=lambda idx=i: remove_split(idx),
                        bg="#444444", fg="#ffffff", width=2)
        btn.pack(side="right", padx=5)

# --------------------
# Manual buttons toggle
# --------------------
def toggle_ui(event=None):
    global ui_visible
    ui_visible = not ui_visible
    if ui_visible:
        control_frame.pack(fill="x", pady=6)
        toggle_btn.config(text="<")
    else:
        control_frame.pack_forget()
        toggle_btn.config(text=">")

# --------------------
# Timer loop
# --------------------
def update_timer():
    if running:
        current = time.time() - start_time
        timer_label.config(text=f"{current:.2f}s", fg="#00ff00")  # green running
    else:
        timer_label.config(fg="#ffffff")  # white when paused
    root.after(10, update_timer)

# --------------------
# Window setup
# --------------------
root = tk.Tk()
root.title("Speedrun Timer")
root.geometry("280x400")
root.configure(bg=UI["bg_color"])
root.attributes("-alpha", UI["opacity"])

# Timer label
timer_label = tk.Label(
    root,
    text="0.00s",
    font=("Arial", 32, "bold"),
    fg="#ffffff",
    bg=UI["bg_color"]
)
timer_label.pack(pady=10)

# Toggle button for manual controls
toggle_btn = tk.Button(root, text=">", width=2, command=toggle_ui, bg="#444444", fg="#ffffff")
toggle_btn.pack()

# Manual control buttons frame
control_frame = tk.Frame(root, bg="#222222")  # slightly lighter than main bg
tk.Button(control_frame, text="Start / Stop", command=toggle_timer,
          bg="#333333", fg="#ffffff").pack(pady=2, fill="x")
tk.Button(control_frame, text="Save Split", command=save_split,
          bg="#333333", fg="#ffffff").pack(pady=2, fill="x")
tk.Button(control_frame, text="Reset Timer", command=reset_timer,
          bg="#333333", fg="#ffffff").pack(pady=2, fill="x")

# Frame to hold split rows
split_list_frame = tk.Frame(root, bg="#222222")
split_list_frame.pack(fill="both", expand=True, padx=8, pady=6)

# --------------------
# Key bindings
# --------------------
root.bind(KEYS["start"], toggle_timer)
root.bind(KEYS["reset"], reset_timer)
root.bind(KEYS["save"], save_split)
root.bind(KEYS["toggle_ui"], toggle_ui)

# --------------------
update_timer()
root.mainloop()
