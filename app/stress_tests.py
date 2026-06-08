import threading
import time
import random

from reservation_service import ReservationService


def stress_test_1(service):

    success = 0
    failure = 0

    start = time.time()

    for _ in range(100):
        if service.reserve_seat(
            "MOV1",
            "A1",
            "SPAMMER"
        ):
            success += 1
        else:            
            failure += 1

    end = time.time()

    print("\n=== STRESS TEST 1 ===")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Time: {end-start:.2f}s")

def stress_test_2(service):

    users = [
        "Kotlowski",
        "Kadzinski",
        "Brzezinski",
        "Ochodek",
        "Stefanowski"
    ]

    seats = [
        f"{row}{num}"
        for row in ["A", "B", "C", "D"]
        for num in range(1, 10)
    ]

    success = 0
    failure = 0

    lock = threading.Lock()

    def random_client(user):

        nonlocal success
        nonlocal failure

        for _ in range(20):

            seat = random.choice(seats)

            result = service.reserve_seat(
                "MOV1",
                seat,
                user
            )

            with lock:

                if result:
                    success += 1
                else:
                    failure += 1

    threads = []

    start = time.time()

    for user in users:

        t = threading.Thread(target=random_client, args=(user,))

        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()

    print("\n=== STRESS TEST 2 ===")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Time: {end-start:.2f}s")

def stress_test_3(service):

    seats = [
        f"{row}{num}"
        for row in ["A", "B", "C", "D"]
        for num in range(1, 11)
    ]

    results = {
        "CLIENT_A": 0,
        "CLIENT_B": 0
    }

    lock = threading.Lock()

    def reserve_all(client_name):

        for seat in seats:

            result = service.reserve_seat(
                "MOV1",
                seat,
                client_name
            )

            if result:

                with lock:
                    results[client_name] += 1

    t1 = threading.Thread(
        target=reserve_all,
        args=("CLIENT_A",)
    )

    t2 = threading.Thread(
        target=reserve_all,
        args=("CLIENT_B",)
    )

    start = time.time()

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    end = time.time()

    print("\n=== STRESS TEST 3 ===")
    print(f"CLIENT_A reserved: {results['CLIENT_A']}")
    print(f"CLIENT_B reserved: {results['CLIENT_B']}")
    print(f"Total: {sum(results.values())}")
    print(f"Time: {end-start:.2f}s")

def stress_test_4(service):

    success = 0
    failure = 0

    start = time.time()

    for _ in range(100):
        if service.reserve_seat(
            "MOV1",
            "A1",
            "SPAMMER"
        ):
            success += 1
        else:            
            failure += 1

        if service.cancel_reservation(
            "MOV1",
            "A1",
            "SPAMMER"
        ):
            success += 1
        else:            
            failure += 1

    end = time.time()

    print("\n=== STRESS TEST 4 ===")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Time: {end-start:.2f}s")

def stress_test_5(service):

    group_user = "GROUP_LEADER"
    
    seats = [
        f"{row}{num}"
        for row in ["A", "B", "C", "D"]
        for num in range(1, 11)
    ]

    success = 0
    failure = 0
    start = time.time()

    for _ in range(10):

        for seat in seats:
            service.reserve_seat(
                "MOV1",
                seat,
                group_user
            )

        if service.cancel_multiple_reservations(
            "MOV1",
            seats,
            group_user
        ):
            success += 1
        else:
            failure += 1

    end = time.time()

    print("\n=== STRESS TEST 5 ===")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Time: {end-start:.2f}s")

def reset_seats(session):

    for row in ["A", "B", "C", "D"]:
        for num in range(1, 11):

            seat = f"{row}{num}"

            session.execute("""
            UPDATE seats
            SET reserved = false,
                reserved_by = null
            WHERE movie_id = %s
              AND seat_id = %s
            """, ("MOV1", seat))