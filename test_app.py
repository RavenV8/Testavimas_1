import sys
sys.path.append('app')  # Prideda 'app' katalogą į modulio paieškos kelią

import unittest
from flask import Flask
from app.main import app  # Importuojame iš app/main.py

class TestCityAPI(unittest.TestCase):
    def setUp(self):
        # Sukuriame testinį Flask app klientą
        self.app = app.test_client()
        self.app.testing = True
        # Išvalome duomenų bazę prieš kiekvieną testą
        self.app.post('/cleanup')

    # Testai miestų registracijai ir gavimui
    def test_register_city_success(self):
        # Testuojame sėkmingą miesto registraciją
        response = self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.assertEqual(response.status_code, 204)

    def test_register_city_missing_data(self):
        # Testuojame, kai trūksta duomenų
        response = self.app.put('/cities', json={'name': 'Vilnius'})  # Trūksta country
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'name and country are required', response.data)

    def test_register_city_duplicate(self):
        # Testuojame bandymą registruoti tą patį miestą du kartus
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'City already exists', response.data)

    def test_get_cities(self):
        # Pirmiausia įdedame duomenis
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.get('/cities')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data[0]['name'], 'Vilnius')
        self.assertEqual(data[0]['country'], 'Lithuania')

    def test_get_cities_empty(self):
        # Testuojame tuščią miestų sąrašą
        response = self.app.get('/cities')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_get_city_by_name(self):
        # Testuojame konkretaus miesto gavimą
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.get('/cities/Vilnius')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Vilnius')
        self.assertEqual(data['country'], 'Lithuania')

    def test_get_city_not_found(self):
        # Testuojame, kai miestas nerandamas
        response = self.app.get('/cities/NonExistentCity')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'City not found', response.data)

    # Testai oro uostų registracijai ir gavimui
    def test_register_airport_success(self):
        # Pirmiausia sukuriame miestą
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        # Registruojame oro uostą
        response = self.app.put('/cities/Vilnius/airports', 
                              json={'code': 'VNO', 'name': 'Vilnius Airport', 
                                    'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.assertEqual(response.status_code, 204)

    def test_register_airport_missing_data(self):
        # Testuojame, kai trūksta privalomų oro uosto duomenų
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.put('/cities/Vilnius/airports', 
                              json={'name': 'Vilnius Airport'})  # Trūksta code
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'code and name are required', response.data)

    def test_register_airport_city_not_found(self):
        # Testuojame bandymą registruoti oro uostą neegzistuojančiame mieste
        response = self.app.put('/cities/NonExistentCity/airports', 
                              json={'code': 'VNO', 'name': 'Vilnius Airport', 
                                    'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'City not found', response.data)

    def test_get_airports_in_city(self):
        # Pirmiausia sukuriame miestą ir oro uostą
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        # Gauname oro uostus
        response = self.app.get('/cities/Vilnius/airports')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['code'], 'VNO')
        self.assertEqual(data[0]['name'], 'Vilnius Airport')

    def test_get_airports_in_city_empty(self):
        # Testuojame tuščią oro uostų sąrašą mieste
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.get('/cities/Vilnius/airports')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_get_airports_city_not_found(self):
        # Testuojame oro uostų gavimą neegzistuojančiame mieste
        response = self.app.get('/cities/NonExistentCity/airports')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'City not found', response.data)

    # Testai skrydžių registracijai
    def test_register_flight_success(self):
        # Sukuriame miestus ir oro uostus
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Kaunas', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.app.put('/cities/Kaunas/airports', 
                    json={'code': 'KUN', 'name': 'Kaunas Airport', 
                          'numberOfTerminals': 1, 'address': 'Oro uosto g. 4'})
        # Registruojame skrydį
        response = self.app.put('/flights', 
                              json={'number': 'FL123', 'fromAirport': 'VNO', 'toAirport': 'KUN', 
                                    'price': 100, 'flightTimeInMinutes': 30, 'operator': 'TestAir'})
        self.assertEqual(response.status_code, 204)

    def test_register_flight_missing_data(self):
        # Testuojame, kai trūksta privalomų skrydžio duomenų
        response = self.app.put('/flights', 
                              json={'number': 'FL123', 'fromAirport': 'VNO', 'toAirport': 'KUN'})  # Trūksta price, flightTimeInMinutes, operator
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required field', response.data)

    def test_register_flight_invalid_airport(self):
        # Testuojame skrydžio registraciją su neegzistuojančiais oro uostais
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        response = self.app.put('/flights', 
                              json={'number': 'FL123', 'fromAirport': 'XXX', 'toAirport': 'YYY', 
                                    'price': 100, 'flightTimeInMinutes': 30, 'operator': 'TestAir'})
        self.assertEqual(response.status_code, 500)  # Tikimės klaidos, nes oro uostai nerandami

    def test_get_flight_by_number(self):
        # Testuojame konkretaus skrydžio gavimą
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.app.put('/flights', 
                    json={'number': 'FL123', 'fromAirport': 'VNO', 'toAirport': 'VNO', 
                          'price': 100, 'flightTimeInMinutes': 30, 'operator': 'TestAir'})
        response = self.app.get('/flights/FL123')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['number'], 'FL123')
        self.assertEqual(data['fromAirport'], 'VNO')

    def test_get_flight_not_found(self):
        # Testuojame, kai skrydis nerandamas
        response = self.app.get('/flights/FL999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Flight not found', response.data)

    # Testai skrydžių paieškai tarp miestų
    def test_search_flights_direct(self):
        # Testuojame tiesioginius skrydžius
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Kaunas', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.app.put('/cities/Kaunas/airports', 
                    json={'code': 'KUN', 'name': 'Kaunas Airport', 
                          'numberOfTerminals': 1, 'address': 'Oro uosto g. 4'})
        self.app.put('/flights', 
                    json={'number': 'FL123', 'fromAirport': 'VNO', 'toAirport': 'KUN', 
                          'price': 100, 'flightTimeInMinutes': 30, 'operator': 'TestAir'})
        response = self.app.get('/search/flights/Vilnius/Kaunas')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['flights']), 1)
        self.assertEqual(data['flights'][0]['fromAirport'], 'VNO')
        self.assertEqual(data['flights'][0]['toAirport'], 'KUN')

    def test_search_flights_no_flights(self):
        # Testuojame, kai skrydžių nerandama
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Kaunas', 'country': 'Lithuania'})
        response = self.app.get('/search/flights/Vilnius/Kaunas')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Flights not found', response.data)

    def test_search_flights_cities_not_found(self):
        # Testuojame, kai vieni ar abu miestai nerandami
        response = self.app.get('/search/flights/NonExistentCity/Kaunas')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Flights not found', response.data)

    # Nauji testai (7 papildomi)

    def test_get_cities_by_country(self):
        # Testuojame miestų filtravimą pagal šalį
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Kaunas', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Riga', 'country': 'Latvia'})
        response = self.app.get('/cities?country=Lithuania')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all(city['country'] == 'Lithuania' for city in data))

    def test_get_airport_by_code(self):
        # Testuojame konkretaus oro uosto gavimą pagal kodą
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        response = self.app.get('/airports/VNO')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['code'], 'VNO')
        self.assertEqual(data['name'], 'Vilnius Airport')

    def test_get_airport_not_found(self):
        # Testuojame, kai oro uostas nerandamas
        response = self.app.get('/airports/XXX')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Airport not found', response.data)

    def test_register_flight_high_price(self):
        # Testuojame skrydžio registraciją su didelė kaina
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        response = self.app.put('/flights', 
                              json={'number': 'FL124', 'fromAirport': 'VNO', 'toAirport': 'VNO', 
                                    'price': 1000, 'flightTimeInMinutes': 60, 'operator': 'LuxAir'})
        self.assertEqual(response.status_code, 204)
        flight = self.app.get('/flights/FL124').get_json()
        self.assertEqual(flight['price'], 1000)

    def test_search_flights_layover(self):
        # Testuojame skrydžius su perlipimais
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Kaunas', 'country': 'Lithuania'})
        self.app.put('/cities', json={'name': 'Riga', 'country': 'Latvia'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.app.put('/cities/Kaunas/airports', 
                    json={'code': 'KUN', 'name': 'Kaunas Airport', 
                          'numberOfTerminals': 1, 'address': 'Oro uosto g. 4'})
        self.app.put('/cities/Riga/airports', 
                    json={'code': 'RIX', 'name': 'Riga Airport', 
                          'numberOfTerminals': 3, 'address': 'Address 3'})
        self.app.put('/flights', 
                    json={'number': 'FL125', 'fromAirport': 'VNO', 'toAirport': 'RIX', 
                          'price': 150, 'flightTimeInMinutes': 90, 'operator': 'TestAir'})
        self.app.put('/flights', 
                    json={'number': 'FL126', 'fromAirport': 'RIX', 'toAirport': 'KUN', 
                          'price': 100, 'flightTimeInMinutes': 60, 'operator': 'TestAir'})
        response = self.app.get('/search/flights/Vilnius/Kaunas')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['flights']), 1)
        self.assertEqual(data['flights'][0]['flights'], ['FL125', 'FL126'])
        self.assertEqual(data['flights'][0]['price'], 250)
        self.assertEqual(data['flights'][0]['flightTimeInMinutes'], 150)

    def test_register_multiple_airports_same_city(self):
        # Testuojame kelių oro uostų registravimą tame pačiame mieste
        self.app.put('/cities', json={'name': 'Vilnius', 'country': 'Lithuania'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'VNO', 'name': 'Vilnius Airport', 
                          'numberOfTerminals': 2, 'address': 'Rodūnios kelias 10A'})
        self.app.put('/cities/Vilnius/airports', 
                    json={'code': 'EYVK', 'name': 'Kyviškės Airport', 
                          'numberOfTerminals': 1, 'address': 'Address 4'})
        response = self.app.get('/cities/Vilnius/airports')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        codes = [airport['code'] for airport in data]
        self.assertIn('VNO', codes)
        self.assertIn('EYVK', codes)

    def test_register_city_invalid_name(self):
        # Testuojame miesto registravimą su neteisingu pavadinimu (pvz., tuštu)
        response = self.app.put('/cities', json={'name': '', 'country': 'Lithuania'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'name and country are required', response.data)

    def tearDown(self):
        # Išvalome duomenų bazę po kiekvieno testo
        self.app.post('/cleanup')

if __name__ == '__main__':
    unittest.main()