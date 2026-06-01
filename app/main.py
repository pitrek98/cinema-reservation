from db import get_session
from reservation_service import ReservationService
from reservation_service import initialize_seats

session = get_session()

initialize_seats(session)

service = ReservationService(session)

while True:

    print("Avaliable movies:")

    movies = service.view_movies() + ["Exit"]
    for i, movie in enumerate(movies, start=1):
        print(i, ". ", movie, sep="")
    
    movie_id = movies[int(input("Select movie by number: ")) - 1]

    if movie_id == "Exit":
        break

    while True:

        print("\n1. Reserve")
        print("2. Update reservation")
        print("3. View reservations")
        print("4. Back to movie selection")

        choice = input("> ")

        if choice == "1":

            user = input("User: ")
            seat = input("Seat: ")

            result = service.reserve_seat(
                movie_id,
                seat,
                user
            )

            if result:
                print(f"[SUCCESS] {user} reserved {seat}")
            else:
                print(f"[FAILED] {seat} could not be reserved")

        elif choice == "2":

            old_user = input("Old user: ")
            new_user = input("New user: ")
            seat = input("Seat: ")

            result = service.update_reservation(
                movie_id,
                seat,
                old_user,
                new_user
            )

            if result:
                print("[UPDATED]")
            else:
                print("[FAILED UPDATE]")
        elif choice == "3":

            reservations = service.get_reservations(movie_id)
            for row in reservations:
                print(row)

        elif choice == "4":
            break