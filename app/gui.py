from db import get_session
from reservation_service import ReservationService
from reservation_service import initialize_seats
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

session = get_session()
initialize_seats(session)
service = ReservationService(session)
movies = service.get_movies()

root = tk.Tk()
root.title("Cinema Reservation System")
root.geometry("1920x1080")

tk.Label(root, text="Cinema seats reservation platform", font=("Arial", 16)).pack()

chosen_movie = tk.StringVar()
reservation_user = tk.StringVar()

seat_frame = tk.Frame(root)
seat_frame.pack(pady=10)

selected_seats = set()
cancel_mode = False  # False = tryb rezerwacji, True = tryb anulowania


def draw_seats():
    movie = chosen_movie.get()
    if not movie:
        return
    rows = service.get_reservations(movie)
    seat_data = {r.seat_id: r for r in rows}
    user = reservation_user.get()
    selected_seats.clear()

    for widget in seat_frame.winfo_children():
        widget.destroy()

    for r, row_letter in enumerate(["A", "B", "C", "D"]):
        for c in range(1, 11):
            seat_id = f"{row_letter}{c}"
            row = seat_data.get(seat_id)
            reserved = row.reserved if row else False
            reserved_by = row.reserved_by if row else None

            if cancel_mode:
                if reserved:
                    # podświetl miejsca należące do obecnego usera
                    color = "orange" if reserved_by == user else "red"
                    state = "normal"
                else:
                    color = "green"
                    state = "disabled"
            else:
                color = "red" if reserved else "green"
                state = "disabled" if reserved else "normal"

            btn = tk.Button(seat_frame, text=seat_id, bg=color, width=4, state=state)
            btn.config(command=lambda s=seat_id, b=btn: toggle_seat(s, b))
            btn.grid(row=r, column=c, padx=2, pady=2)


def toggle_seat(seat_id, btn):
    if cancel_mode:
        if seat_id in selected_seats:
            selected_seats.remove(seat_id)
            # przywróć oryginalny kolor
            movie = chosen_movie.get()
            rows = service.get_reservations(movie)
            seat_data = {r.seat_id: r for r in rows}
            row = seat_data.get(seat_id)
            user = reservation_user.get()
            color = "orange" if row and row.reserved_by == user else "red"
            btn.config(bg=color)
        else:
            selected_seats.add(seat_id)
            btn.config(bg="yellow")
    else:
        if seat_id in selected_seats:
            selected_seats.remove(seat_id)
            btn.config(bg="green")
        else:
            selected_seats.add(seat_id)
            btn.config(bg="yellow")


def on_movie_select(event):
    draw_seats()


def toggle_cancel_mode():
    global cancel_mode
    cancel_mode = not cancel_mode
    cancel_mode_btn.config(
        text="Tryb anulowania" if not cancel_mode else "Tryb zajmowania",
        bg="orange" if not cancel_mode else "blue"
    )
    draw_seats()


def reserve():
    global cancel_mode
    movie = chosen_movie.get()
    user = reservation_user.get()
    if not movie or not user or not selected_seats:
        messagebox.showwarning("Błąd", "Wybierz film, podaj imię i zaznacz miejsca.")
        return
    cancel_mode = False
    cancel_mode_btn.config(text="Tryb anulowania", bg="orange")
    for seat in list(selected_seats):
        service.reserve_seat(movie, seat, user)
    messagebox.showinfo("OK", f"Zarezerwowano: {', '.join(sorted(selected_seats))}")
    draw_seats()


def cancel():
    global cancel_mode
    movie = chosen_movie.get()
    user = reservation_user.get()
    if not movie or not user or not selected_seats:
        messagebox.showwarning("Błąd", "Wybierz film, podaj imię i zaznacz miejsca.")
        return
    service.cancel_multiple_reservations(movie, selected_seats, user)
    messagebox.showinfo("OK", f"Anulowano: {', '.join(sorted(selected_seats))}")
    cancel_mode = False
    cancel_mode_btn.config(text="Tryb anulowania", bg="orange")
    draw_seats()


input_movie = ttk.Combobox(root, values=movies, textvariable=chosen_movie)
input_movie.bind("<<ComboboxSelected>>", on_movie_select)
input_movie.pack()

tk.Label(root, text="Imię:").pack()
tk.Entry(root, width=30, textvariable=reservation_user).pack()

tk.Label(root, textvariable=chosen_movie, font=("Arial", 12)).pack()

tk.Button(root, text="Rezerwuj", command=reserve, bg="blue", fg="white").pack(pady=5)
cancel_mode_btn = tk.Button(root, text="Tryb anulowania", command=toggle_cancel_mode, bg="orange", fg="white")
cancel_mode_btn.pack(pady=2)
tk.Button(root, text="Anuluj zaznaczone", command=cancel, bg="red", fg="white").pack()

root.mainloop()