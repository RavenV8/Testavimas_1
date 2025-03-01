Paleidimas
docker-compose up --build
python3 -m unittest test_app.py -v

test_get_flight_by_number - skrydis pagal numerį
test_register_flight_invalid_airport - neegzistuojantis oro uostas
test_get_flight_by_date - skrydis pagal datą
test_register_flight_duplicate - dubliuotas skrydis
test_cancel_flight - atšaukti skrydį
test_get_flights_by_destination - skrydžiai pagal paskirties vietą
test_register_flight_invalid_time - neteisingas skrydžio laikas
test_register_flight_missing_info - trūksta informacijos apie skrydį
test_get_flight_by_airline - skrydis pagal aviakompaniją
test_update_flight_time - atnaujinti skrydžio laiką
test_register_passenger - registruoti keleivį
test_check_in_passenger - keleivio įregistravimas
test_check_in_passenger_invalid - neteisingas keleivio įregistravimas
test_get_passenger_details - gauti keleivio informaciją
test_cancel_passenger - atšaukti keleivį
test_add_baggage - pridėti bagažą
test_remove_baggage - pašalinti bagažą
test_get_baggage_info - gauti bagažo informaciją
test_booking_system_error - sistemos klaida užsakymo metu
test_register_airline - registruoti aviakompaniją
test_update_airline_info - atnaujinti aviakompanijos informaciją
test_get_airline_info - gauti aviakompanijos informaciją
test_register_flight_with_invalid_date - skrydis su neteisinga data
test_get_flight_by_passenger - skrydis pagal keleivį
test_check_passenger_baggage - tikrinti keleivio bagažą
test_cancel_airline - atšaukti aviakompaniją
test_get_flight_by_baggage - skrydis pagal bagažą
test_update_passenger_info - atnaujinti keleivio informaciją
test_register_passenger_invalid_info - neteisinga keleivio informacija
