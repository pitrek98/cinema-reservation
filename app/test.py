from db import get_session
from reservation_service import ReservationService
from reservation_service import initialize_seats
import time

from stress_tests import (
    stress_test_1,
    stress_test_2,
    stress_test_3,
    stress_test_4,
    reset_seats,
    stress_test_5
)

session = get_session()

initialize_seats(session)

service = ReservationService(session)

reset_seats(session)
time.sleep(3)
stress_test_1(service)

reset_seats(session)
time.sleep(3)
stress_test_2(service)

reset_seats(session)
time.sleep(3)
stress_test_3(service)

reset_seats(session)
time.sleep(3)
stress_test_4(service)

reset_seats(session)
time.sleep(3)
stress_test_5(service)