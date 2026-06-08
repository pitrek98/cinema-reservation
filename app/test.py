from db import get_session
from reservation_service import ReservationService
from reservation_service import initialize_seats
import time

from stress_tests import (
    stress_test_1,
    stress_test_2,
    stress_test_3,
    reset_seats
)

session = get_session()

initialize_seats(session)

service = ReservationService(session)

reset_seats(session)
time.sleep(5)
stress_test_1(service)

reset_seats(session)
time.sleep(5)
stress_test_2(service)

reset_seats(session)
time.sleep(5)
stress_test_3(service)