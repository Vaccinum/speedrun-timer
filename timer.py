import time
import tkinter as tk

running = False
start_time = 0.0
elapsed = 0.0
laps = []

def format_time(seconds):
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02}:{s:05.2f}"

def current_time():
    if running:
        return elapsed + (time.time() - start_time)
    return elapsed

def update():
    timer_label.config(text=format_time(current_time()))
    root.after(10, update)

def toggle():
    global running, start_time, elapsed
    if running:
        elapsed += time.time() - start_time
        running = False
    else:
        start_time = time.time()
        running = True

def save_lap(event=None):
    t = current_time()
    laps.append(t)
    lap_list.insert(tk.END, f"{len(laps):02}  {format_time(t)}")
    update_sum()

def reset(event=None):
    global running, elapsed, laps
    running = False
    elapsed = 0.0
    laps = []
    lap_list.delete(0, tk.END)
    timer_label.config(text="00:00.00")
    sum_label.config(text="Sum: 00:00.00")

def update_sum():
    total = sum(laps)
    sum_label.config(text=f"Sum: {format_time(total)}")

# ── UI ─────────────────────────────
root = tk.Tk()
root.title("Simple Speedrun Timer")
root.geometry("300x400")
root.configure(bg="#111")

timer_label = tk.Label(
    root, text="00:00.00",
    font=("Arial", 32),
    fg="white", bg="#111"
)
timer_label.pack(pady=10)

lap_list = tk.Listbox(
    root, font=("Arial", 12),
    bg="#1a1a1a", fg="white"
)
lap_list.pack(expand=True, fill="both", padx=10)

sum_label = tk.Label(
    root, text="Sum: 00:00.00",
    font=("Arial", 14),
    fg="white", bg="#111"
)
sum_label.pack(pady=5)

# ── Key binds (simple & safe) ───────
root.bind("<space>", lambda e: toggle())
root.bind("<Return>", save_lap)
root.bind("r", reset)

update()
root.mainloop()
