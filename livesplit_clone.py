import tkinter as tk
import time

# --------------------
# Timer state
# --------------------
running = False
start_time = 0
elapsed = 0

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
    global running, start_time, elapsed
    running = False
    start_time = 0
    elapsed = 0
    timer_label.config(text="0.00s")

# --------------------
# UI update loop
# --------------------
def update_timer():
    if running:
        current = time.time() - start_time
        timer_label.config(text=f"{current:.2f}s")
    root.after(10, update_timer)

# --------------------
# Window
# --------------------
root = tk.Tk()
root.title("Speedrun Timer")
root.geometry("300x160")
root.configure(bg="#0b0b0b")

# --------------------
# Timer display
# --------------------
timer_label = tk.Label(
    root,
    text="0.00s",
    font=("Arial", 32, "bold"),
    fg="#00ff88",
    bg="#0b0b0b"
)
timer_label.pack(pady=15)

# --------------------
# Buttons
# --------------------
btn_frame = tk.Frame(root, bg="#0b0b0b")
btn_frame.pack()

start_btn = tk.Button(
    btn_frame,
    text="Start / Split",
    width=12,
    command=toggle_timer
)
start_btn.grid(row=0, column=0, padx=5)

reset_btn = tk.Button(
    btn_frame,
    text="Reset",
    width=12,
    command=reset_timer
)
reset_btn.grid(row=0, column=1, padx=5)

# --------------------
# Key bindings (NO ROOT NEEDED)
# --------------------
root.bind("<space>", toggle_timer)   # Space = Start / Split
root.bind("<r>", reset_timer)        # R = Reset

# --------------------
# Start loop
# --------------------
update_timer()
root.mainloop()
