https://youtu.be/kipdwTYuuZA
Programa yra skirta skrydžiams tikrinti

Paleidimas
docker-compose up --build
python3 -m unittest test_app.py -v

1. **test_get_flight_by_number** - skrydis pagal numerį  
2. **test_register_flight_invalid_airport** - neegzistuojantis oro uostas  
3. **test_get_flight_by_date** - skrydis pagal datą  
4. **test_register_flight_duplicate** - dubliuotas skrydis  
5. **test_cancel_flight** - atšaukti skrydį  
6. **test_get_flights_by_destination** - skrydžiai pagal paskirties vietą  
7. **test_register_flight_invalid_time** - neteisingas skrydžio laikas  
8. **test_register_flight_missing_info** - trūksta informacijos apie skrydį  
9. **test_get_flight_by_airline** - skrydis pagal aviakompaniją  
10. **test_update_flight_time** - atnaujinti skrydžio laiką  
11. **test_register_passenger** - registruoti keleivį  
12. **test_check_in_passenger** - keleivio įregistravimas  
13. **test_check_in_passenger_invalid** - neteisingas keleivio įregistravimas  
14. **test_get_passenger_details** - gauti keleivio informaciją  
15. **test_cancel_passenger** - atšaukti keleivį  
16. **test_add_baggage** - pridėti bagažą  
17. **test_remove_baggage** - pašalinti bagažą  
18. **test_get_baggage_info** - gauti bagažo informaciją  
19. **test_booking_system_error** - sistemos klaida užsakymo metu  
20. **test_register_airline** - registruoti aviakompaniją  
21. **test_update_airline_info** - atnaujinti aviakompanijos informaciją  
22. **test_get_airline_info** - gauti aviakompanijos informaciją  
23. **test_register_flight_with_invalid_date** - skrydis su neteisinga data  
24. **test_get_flight_by_passenger** - skrydis pagal keleivį  
25. **test_check_passenger_baggage** - tikrinti keleivio bagažą  
26. **test_cancel_airline** - atšaukti aviakompaniją  
27. **test_get_flight_by_baggage** - skrydis pagal bagažą  
28. **test_update_passenger_info** - atnaujinti keleivio informaciją  
29. **test_register_passenger_invalid_info** - neteisinga keleivio informacija

