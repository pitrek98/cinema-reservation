from db import get_session
from reservation_service import ReservationService
from reservation_service import initialize_seats

session = get_session()

initialize_seats(session)

service = ReservationService(session)

while True:

    print("\n1. Reserve")
    print("2. Update")
    print("3. View")
    print("4. Exit")

    choice = input("> ")

    if choice == "1":

        user = input("User: ")
        seat = input("Seat: ")

        service.reserve_seat(
            "MOV1",
            seat,
            user
        )

    elif choice == "2":

        old_user = input("Old user: ")
        new_user = input("New user: ")
        seat = input("Seat: ")

        service.update_reservation(
            "MOV1",
            seat,
            old_user,
            new_user
        )

    elif choice == "3":

        service.view_reservations("MOV1")

    elif choice == "4":
        break