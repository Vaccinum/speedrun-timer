import time
import tkinter as tk

# ───────── State ─────────
running = False
start_time = 0.0
elapsed = 0.0

# ───────── Helpers ─────────
def now():
    if running:
        return elapsed + (time.time() - start_time)
    return elapsed

def format_time(t):
    return f"{t:0.2f}s"

# ───────── Actions ─────────
def toggle_timer(event=None):
    global running, start_time, elapsed
    if running:
        elapsed += time.time() - start_time
        running = False
    else:
        start_time = time.time()
        running = True

def reset_timer(event=None):
    global running, elapsed
    running = False
    elapsed = 0.0
    label.config(text="0.00s")

def update():
    label.config(text=format_time(now()))
    root.after(16, update)

def close_app(event=None):
    root.destroy()

# ───────── UI ─────────
root = tk.Tk()
root.title("Speedrun Timer")
root.geometry("300x120")
root.configure(bg="#0f0f0f")

label = tk.Label(
    root,
    text="0.00s",
    font=("Arial Black", 36),
    fg="#00ff88",
    bg="#0f0f0f"
)
label.pack(expand=True)

# ───────── Keybinds (window-focused) ─────────
root.bind("<Return>", toggle_timer)     # Enter
root.bind("5", toggle_timer)            # 5 also toggles
root.bind("<BackSpace>", reset_timer)   # Reset
root.bind("<Escape>", close_app)        # Exit safely

update()
root.mainloop()
