from datetime import datetime

from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
from cassandra.query import BatchStatement
from cassandra.query import BatchType

class ReservationService:

    def __init__(self, session):
        self.session = session

    def get_movies(self):
        try:
            query = """
            SELECT DISTINCT movie_id FROM seats;
            """

            rows = self.session.execute(query)

            movies = [row.movie_id for row in rows]

            return movies
        except Exception as e:
            print(f"[ERROR] {e}")
            return []

    def reserve_seat(self, movie_id, seat_id, user):

        try:
            query = self.session.prepare("""
            UPDATE seats
            SET reserved = true,
                reserved_by = ?,
                reservation_time = ?
            WHERE movie_id = ?
            AND seat_id = ?
            IF reserved = false;
            """)

            query.consistency_level = ConsistencyLevel.QUORUM
            query.serial_consistency_level = ConsistencyLevel.SERIAL

            result = self.session.execute(
                query,
                (user, datetime.now(), movie_id, seat_id)
            )

            row = result.one()

            return row.applied
        except Exception as e:
            print(f"[ERROR] {e}")
            return False



    def get_reservations(self, movie_id):
        try:
            query = """
            SELECT * FROM seats
            WHERE movie_id = %s;
            """

            rows = self.session.execute(query, (movie_id,))

            return rows
        except Exception as e:
            print(f"[ERROR] {e}")
            return []

    def update_reservation(self, movie_id, seat_id, old_user, new_user):
        try:
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
            return row.applied
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
        
    def cancel_reservation(self, movie_id, seat_id, user):
        try:
            query = """
            UPDATE seats
            SET reserved = false,
                reserved_by = null,
                reservation_time = null
            WHERE movie_id = %s
            AND seat_id = %s
            IF reserved_by = %s;
            """

            result = self.session.execute(
                query,
                (movie_id, seat_id, user)
            )

            row = result.one()
            return row.applied
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
        
    def cancel_multiple_reservations(self, movie_id, seat_ids, user):
        try:
            batch = BatchStatement()
            for seat_id in seat_ids:
                query = """
                UPDATE seats
                SET reserved = false,
                    reserved_by = null,
                    reservation_time = null
                WHERE movie_id = %s
                AND seat_id = %s
                IF reserved_by = %s;
                """
                batch.add(SimpleStatement(query), (movie_id, seat_id, user))

            result = self.session.execute(batch)

            return all(row.applied for row in result)
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

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