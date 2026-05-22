from datetime import datetime

class ReservationService:

    def __init__(self, session):
        self.session = session

    def view_movies(self):

        query = """
        SELECT DISTINCT movie_id FROM seats;
        """

        rows = self.session.execute(query)

        movies = [row.movie_id for row in rows]

        return movies

    def reserve_seat(self, movie_id, seat_id, user):

        query = """
        UPDATE seats
        SET reserved = true,
            reserved_by = %s,
            reservation_time = %s
        WHERE movie_id = %s
          AND seat_id = %s
        IF reserved = false;
        """

        result = self.session.execute(
            query,
            (user, datetime.now(), movie_id, seat_id)
        )

        row = result.one()

        if row.applied:
            print(f"[SUCCESS] {user} reserved {seat_id}")
            return True
        else:
            print(f"[FAILED] {seat_id} could not be reserved")
            return False

    def view_reservations(self, movie_id):

        query = """
        SELECT * FROM seats
        WHERE movie_id = %s;
        """

        rows = self.session.execute(query, (movie_id,))

        for row in rows:
            print(row)

    def update_reservation(self, movie_id, seat_id, old_user, new_user):

        query = """
        UPDATE seats
        SET reserved_by = %s
        WHERE movie_id = %s
          AND seat_id = %s
        IF reserved_by = %s;
        """

        result = self.session.execute(
            query,
            (new_user, movie_id, seat_id, old_user)
        )

        row = result.one()

        if row.applied:
            print("[UPDATED]")
        else:
            print("[FAILED UPDATE]")

def initialize_seats(session):
    for movie_id in ["MOV1", "MOV2", "MOV3"]:
        for row_letter in ["A", "B", "C", "D"]:
            for num in range(1, 11):

                seat_id = f"{row_letter}{num}"

                session.execute("""
                INSERT INTO seats (
                    movie_id,
                    seat_id,
                    reserved,
                    reserved_by
                )
                VALUES (%s, %s, false, null)
                IF NOT EXISTS
                """, (movie_id, seat_id))