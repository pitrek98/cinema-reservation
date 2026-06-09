import tkinter as tk
from tkinter import messagebox, ttk

from db import get_session
from reservation_service import ReservationService, initialize_seats

session = get_session()
initialize_seats(session)
service = ReservationService(session)

root = tk.Tk()
root.title("Cinema Reservation System")
root.geometry("900x700")

tk.Label(root, text="Cinema Reservation System", font=("Arial", 16)).pack(pady=10)

chosen_movie = tk.StringVar()
selected_seats: set[str] = set()
current_mode = tk.StringVar(value="reserve")

top_frame = tk.Frame(root)
top_frame.pack(pady=5)

tk.Label(top_frame, text="Movie:").grid(row=0, column=0, padx=4)
movies = service.get_movies()
movie_box = ttk.Combobox(top_frame, values=movies, textvariable=chosen_movie, width=20)
movie_box.grid(row=0, column=1, padx=4)

tk.Label(top_frame, text="Your name:").grid(row=0, column=2, padx=4)
user_var = tk.StringVar()
tk.Entry(top_frame, textvariable=user_var, width=20).grid(row=0, column=3, padx=4)

mode_frame = tk.Frame(root)
mode_frame.pack(pady=5)


def set_mode(mode: str) -> None:
    current_mode.set(mode)
    selected_seats.clear()
    draw_seats()
    for btn in mode_buttons.values():
        btn.config(relief="raised", bg="SystemButtonFace")
    mode_buttons[mode].config(relief="sunken", bg="lightblue")


mode_buttons: dict[str, tk.Button] = {}
for label, mode in [("Reserve", "reserve"), ("Update reservation", "update"), ("Cancel", "cancel")]:
    b = tk.Button(mode_frame, text=label, width=18, command=lambda m=mode: set_mode(m))
    b.pack(side="left", padx=4)
    mode_buttons[mode] = b
mode_buttons["reserve"].config(relief="sunken", bg="lightblue")

seat_frame = tk.Frame(root)
seat_frame.pack(pady=10)

legend_frame = tk.Frame(root)
legend_frame.pack()
for color, label in [("green", "Free"), ("red", "Taken"), ("orange", "Yours"), ("yellow", "Selected")]:
    tk.Label(legend_frame, text=f"  {label}  ", bg=color, relief="groove").pack(side="left", padx=3)


def draw_seats() -> None:
    movie = chosen_movie.get()
    if not movie:
        return
    user = user_var.get().strip()
    rows = service.get_reservations(movie)
    seat_data = {r.seat_id: r for r in rows}
    selected_seats.clear()

    for widget in seat_frame.winfo_children():
        widget.destroy()

    mode = current_mode.get()

    for r, row_letter in enumerate(["A", "B", "C", "D"]):
        tk.Label(seat_frame, text=row_letter, width=2).grid(row=r, column=0)
        for c in range(1, 11):
            seat_id = f"{row_letter}{c}"
            row = seat_data.get(seat_id)
            reserved = row.reserved if row else False
            reserved_by = row.reserved_by if row else None

            if mode == "reserve":
                color = "red" if reserved else "green"
                state = "disabled" if reserved else "normal"
            elif mode == "update":
                is_mine = reserved and reserved_by == user
                color = "orange" if is_mine else ("red" if reserved else "green")
                state = "normal" if is_mine else "disabled"
            elif mode == "cancel":
                is_mine = reserved and reserved_by == user
                color = "orange" if is_mine else ("red" if reserved else "green")
                state = "normal" if is_mine else "disabled"
            else:
                color, state = "green", "normal"

            btn = tk.Button(seat_frame, text=seat_id, bg=color, width=5, state=state)
            btn.config(command=lambda s=seat_id, b=btn, orig=color: toggle_seat(s, b, orig))
            btn.grid(row=r, column=c + 1, padx=2, pady=2)


def toggle_seat(seat_id: str, btn: tk.Button, original_color: str) -> None:
    if seat_id in selected_seats:
        selected_seats.remove(seat_id)
        btn.config(bg=original_color)
    else:
        selected_seats.add(seat_id)
        btn.config(bg="yellow")


def on_movie_select(_event=None) -> None:
    selected_seats.clear()
    draw_seats()


movie_box.bind("<<ComboboxSelected>>", on_movie_select)

action_frame = tk.Frame(root)
action_frame.pack(pady=10)


def do_reserve() -> None:
    movie = chosen_movie.get()
    user = user_var.get().strip()
    if not movie or not user or not selected_seats:
        messagebox.showwarning("Missing info", "Select a movie, enter your name, and pick seats.")
        return
    succeeded, failed = [], []
    for seat in sorted(selected_seats):
        if service.reserve_seat(movie, seat, user):
            succeeded.append(seat)
        else:
            failed.append(seat)
    msg = ""
    if succeeded:
        msg += f"Reserved: {', '.join(succeeded)}\n"
    if failed:
        msg += f"Already taken: {', '.join(failed)}"
    messagebox.showinfo("Result", msg.strip())
    set_mode("reserve")


def do_cancel() -> None:
    movie = chosen_movie.get()
    user = user_var.get().strip()
    if not movie or not user or not selected_seats:
        messagebox.showwarning("Missing info", "Select a movie, enter your name, and pick seats.")
        return
    succeeded, failed = [], []
    for seat in sorted(selected_seats):
        if service.cancel_reservation(movie, seat, user):
            succeeded.append(seat)
        else:
            failed.append(seat)
    msg = ""
    if succeeded:
        msg += f"Cancelled: {', '.join(succeeded)}\n"
    if failed:
        msg += f"Could not cancel (wrong name?): {', '.join(failed)}"
    messagebox.showinfo("Result", msg.strip())
    set_mode("reserve")


update_frame = tk.Frame(root)
tk.Label(update_frame, text="New name:").pack(side="left")
new_user_var = tk.StringVar()
tk.Entry(update_frame, textvariable=new_user_var, width=20).pack(side="left", padx=4)


def do_update() -> None:
    movie = chosen_movie.get()
    old_user = user_var.get().strip()
    new_user = new_user_var.get().strip()
    if not movie or not old_user or not new_user or not selected_seats:
        messagebox.showwarning("Missing info", "Fill in your name, new name, and pick a seat.")
        return
    if len(selected_seats) > 1:
        messagebox.showwarning("Too many seats", "Update one seat at a time.")
        return
    seat = next(iter(selected_seats))
    if service.update_reservation(movie, seat, old_user, new_user):
        messagebox.showinfo("Result", f"Seat {seat} transferred to {new_user}.")
    else:
        messagebox.showerror("Failed", "Could not update — check that the name matches the reservation.")
    new_user_var.set("")
    set_mode("reserve")


def refresh_action_panel(*_) -> None:
    for w in action_frame.winfo_children():
        w.destroy()
    update_frame.pack_forget()

    mode = current_mode.get()
    if mode == "reserve":
        tk.Button(action_frame, text="Confirm reservation", bg="blue", fg="white",
                  width=22, command=do_reserve).pack()
    elif mode == "cancel":
        tk.Button(action_frame, text="Confirm cancellation", bg="red", fg="white",
                  width=22, command=do_cancel).pack()
    elif mode == "update":
        update_frame.pack(pady=4)
        tk.Button(action_frame, text="Confirm update", bg="purple", fg="white",
                  width=22, command=do_update).pack()


current_mode.trace_add("write", refresh_action_panel)
refresh_action_panel()

root.mainloop()