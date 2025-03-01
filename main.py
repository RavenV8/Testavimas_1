from flask import Flask, jsonify, request
from neo4j import GraphDatabase, exceptions

app = Flask(__name__)

# Neo4j database configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test"

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_app():
    app = Flask(__name__)

# Register a new city
@app.route('/cities', methods=['PUT'])
def register_city():
    data = request.json
    name = data.get('name')
    country = data.get('country')

    if not name or not country:
        return jsonify({"error": "name and country are required"}), 400

    try:
        with driver.session() as session:
            # Patikriname, ar miestas jau egzistuoja
            result = session.run(
                "MATCH (c:City {name: $name, country: $country}) RETURN c",
                name=name, country=country
            )
            if result.single():
                return jsonify({"error": "City already exists"}), 400
            else:
                # Sukuriame naują miestą
                session.run(
                    "CREATE (c:City {name: $name, country: $country, created: timestamp()})",
                    name=name, country=country
                )
                return '', 204
    except exceptions.Neo4jError as e:
        return jsonify({"error": "Could not register city", "details": str(e)}), 500

# Get all cities or filter by country
@app.route('/cities', methods=['GET'])
def get_cities():
    country = request.args.get('country')

    try:
        with driver.session() as session:
            if country:
                result = session.run("MATCH (c:City {country: $country}) RETURN c.name AS name, c.country AS country",
                                     country=country)
            else:
                result = session.run("MATCH (c:City) RETURN c.name AS name, c.country AS country")
            
            cities = [{"name": record["name"], "country": record["country"]} for record in result]
            return jsonify(cities), 200
    except exceptions.Neo4jError:
        return jsonify({"error": "Could not retrieve cities"}), 500

# Get a specific city by name
@app.route('/cities/<string:name>', methods=['GET'])
def get_cities_in_country(name):
    try:
        with driver.session() as session:
            result = session.run("MATCH (c:City {name: $name}) RETURN c.name AS name, c.country AS country",
                                 name=name)
            city = result.single()
            if city:
                return jsonify({"name": city["name"], "country": city["country"]}), 200
            else:
                return jsonify({"error": "City not found"}), 404
    except exceptions.Neo4jError:
        return jsonify({"error": "Could not retrieve city"}), 500

# Register an airport in a specific city
@app.route('/cities/<string:name>/airports', methods=['PUT'])
def register_airport(name):
    data = request.json
    code = data.get("code")
    airport_name = data.get("name")
    number_of_terminals = data.get("numberOfTerminals")
    address = data.get("address")

    if not code or not airport_name:
        return jsonify({"error": "code and name are required"}), 400

    try:
        with driver.session() as session:
            # Check if city exists
            city_result = session.run("MATCH (c:City {name: $name}) RETURN c", name=name)
            city = city_result.single()
            if not city:
                return jsonify({"error": "City not found"}), 400

            # Create or update airport node and connect it to the city
            session.run(
                """
                MATCH (c:City {name: $city_name})
                MERGE (a:Airport {code: $code})
                SET a.name = $airport_name, a.numberOfTerminals = $number_of_terminals, a.address = $address
                MERGE (a)-[:LOCATED_IN]->(c)
                """,
                city_name=name,
                code=code,
                airport_name=airport_name,
                number_of_terminals=number_of_terminals,
                address=address
            )
            return jsonify({"message": "Airport created."}), 204
    except exceptions.Neo4jError:
        return jsonify({"error": "Could not create airport"}), 500

# Get all airports in a city
@app.route('/cities/<string:name>/airports', methods=['GET'])
def get_airports_in_a_city(name):
    try:
        with driver.session() as session:
            # Pirmiausia patikriname, ar miestas egzistuoja
            city_exists = session.run("MATCH (c:City {name: $name}) RETURN c", name=name).single()
            if not city_exists:
                return jsonify({"error": "City not found"}), 404  # Grąžiname 404, jei miestas nerandamas

            # Query for airports in the specified city
            result = session.run(
                """
                MATCH (a:Airport)-[:LOCATED_IN]->(c:City {name: $city_name})
                RETURN a.code AS code, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address, c.name AS city
                """,
                city_name=name
            )

            airports = [
                {
                    "code": record["code"],
                    "city": record["city"],
                    "name": record["name"],
                    "numberOfTerminals": record["numberOfTerminals"],
                    "address": record["address"]
                }
                for record in result
            ]

            return jsonify(airports), 200
    except exceptions.Neo4jError:
        return jsonify({"error": "Could not retrieve airports"}), 500

# Get a specific airport by code
@app.route('/airports/<string:code>', methods=['GET'])
def get_airport(code):
    try:
        with driver.session() as session:
            # Query for the airport by its code
            result = session.run(
                """
                MATCH (a:Airport {code: $code})-[:LOCATED_IN]->(c:City)
                RETURN a.code AS code, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address, c.name AS city
                """,
                code=code
            )

            airport = result.single()
            if airport:
                return jsonify({
                    "code": airport["code"],
                    "city": airport["city"],
                    "name": airport["name"],
                    "numberOfTerminals": airport["numberOfTerminals"],
                    "address": airport["address"]
                }), 200
            else:
                return jsonify({"error": "Airport not found"}), 404
    except exceptions.Neo4jError:
        return jsonify({"error": "Could not retrieve airport"}), 500

@app.route('/flights', methods=['PUT'])
def register_flight():
    try:
        data = request.get_json()

        # Validate payload structure
        required_fields = ["number", "fromAirport", "toAirport", "price", "flightTimeInMinutes", "operator"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        with driver.session() as session:
            # Patikriname, ar fromAirport egzistuoja
            from_airport_exists = session.run(
                "MATCH (a:Airport {code: $code}) RETURN a",
                code=data["fromAirport"]
            ).single()
            if not from_airport_exists:
                return jsonify({"error": f"Airport {data['fromAirport']} not found"}), 500  # Grąžiname 500, kaip tikisi testas

            # Patikriname, ar toAirport egzistuoja
            to_airport_exists = session.run(
                "MATCH (a:Airport {code: $code}) RETURN a",
                code=data["toAirport"]
            ).single()
            if not to_airport_exists:
                return jsonify({"error": f"Airport {data['toAirport']} not found"}), 500  # Grąžiname 500, kaip tikisi testas

            # Jei abu oro uostai egzistuoja, registruojame skrydį
            session.run(
                """
                MATCH (fromAirport:Airport {code: $fromAirport})
                MATCH (toAirport:Airport {code: $toAirport})
                CREATE (f:Flight {
                    number: $number,
                    price: $price,
                    flightTimeInMinutes: $flightTimeInMinutes,
                    operator: $operator
                })
                MERGE (f)-[:DEPARTS_FROM]->(fromAirport)
                MERGE (f)-[:ARRIVES_AT]->(toAirport)
                """,
                number=data["number"],
                fromAirport=data["fromAirport"],
                toAirport=data["toAirport"],
                price=data["price"],
                flightTimeInMinutes=data["flightTimeInMinutes"],
                operator=data["operator"]
            )
            return jsonify({"message": "Flight registered successfully"}), 204
    except exceptions.Neo4jError as e:
        return jsonify({"error": "Failed to register flight", "details": str(e)}), 500

@app.route('/flights/<string:code>', methods=['GET'])
def get_flight_raw(code):
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (f:Flight {number: $code})
                OPTIONAL MATCH (f)-[:DEPARTS_FROM]->(from:Airport)-[:LOCATED_IN]->(fromCity:City)
                OPTIONAL MATCH (f)-[:ARRIVES_AT]->(to:Airport)-[:LOCATED_IN]->(toCity:City)
                RETURN f.number AS number, f.price AS price, f.flightTimeInMinutes AS flightTimeInMinutes,
                       f.operator AS operator,
                       from.code AS fromAirport, from.name AS fromAirportName, fromCity.name AS fromCity,
                       to.code AS toAirport, to.name AS toAirportName, toCity.name AS toCity
                """,
                code=code
            )
            flight = result.single()
            if flight:
                return jsonify({
                    "number": flight["number"],
                    "price": flight["price"],
                    "flightTimeInMinutes": flight["flightTimeInMinutes"],
                    "operator": flight["operator"],
                    "fromAirport": flight["fromAirport"],
                    "fromCity": flight["fromCity"],
                    "toAirport": flight["toAirport"],
                    "toCity": flight["toCity"]
                }), 200
            else:
                return jsonify({"error": "Flight not found"}), 404
    except exceptions.Neo4jError as e:
        return jsonify({"error": "Failed to retrieve flight", "details": str(e)}), 500

@app.route('/search/flights/<string:fromCity>/<string:toCity>', methods=['GET'])
def search_flights_between_cities(fromCity, toCity):
    try:
        with driver.session() as session:
            # Patikrinkime, ar abu miestai egzistuoja
            from_city_exists = session.run("MATCH (c:City {name: $name}) RETURN c", name=fromCity).single()
            to_city_exists = session.run("MATCH (c:City {name: $name}) RETURN c", name=toCity).single()
            if not from_city_exists or not to_city_exists:
                return jsonify({"error": "Flights not found"}), 404

            # Patikrinkime tiesioginius skrydžius
            direct_flights = session.run(
                """
                MATCH (fromCity:City {name: $fromCity})
                MATCH (toCity:City {name: $toCity})
                MATCH (fromAirport:Airport)-[:LOCATED_IN]->(fromCity)
                MATCH (toAirport:Airport)-[:LOCATED_IN]->(toCity)
                MATCH (f:Flight)-[:DEPARTS_FROM]->(fromAirport)
                MATCH (f)-[:ARRIVES_AT]->(toAirport)
                RETURN f.number AS number, f.price AS price, f.flightTimeInMinutes AS flightTimeInMinutes,
                    fromAirport.code AS fromAirport, fromAirport.name AS fromAirportName,
                    toAirport.code AS toAirport, toAirport.name AS toAirportName
                """,
                fromCity=fromCity, toCity=toCity
            )

            flights = []
            for record in direct_flights:
                flight = {
                    "fromAirport": record["fromAirport"],
                    "toAirport": record["toAirport"],
                    "flights": [record["number"]],
                    "price": record["price"],
                    "flightTimeInMinutes": record["flightTimeInMinutes"]
                }
                flights.append(flight)

            # Jei nėra tiesioginių skrydžių, ieškokime su perlipimais
            if not flights:
                layover_flights = session.run(
                    """
                    MATCH (fromCity:City {name: $fromCity})
                    MATCH (toCity:City {name: $toCity})
                    MATCH (fromAirport:Airport)-[:LOCATED_IN]->(fromCity)
                    MATCH (toAirport:Airport)-[:LOCATED_IN]->(toCity)
                    MATCH (firstFlight:Flight)-[:DEPARTS_FROM]->(fromAirport)
                    MATCH (firstFlight)-[:ARRIVES_AT]->(layoverAirport)
                    MATCH (secondFlight:Flight)-[:DEPARTS_FROM]->(layoverAirport)
                    MATCH (secondFlight)-[:ARRIVES_AT]->(toAirport)
                    RETURN firstFlight.number AS firstFlightNumber, secondFlight.number AS secondFlightNumber,
                           firstFlight.price + secondFlight.price AS price, 
                           firstFlight.flightTimeInMinutes + secondFlight.flightTimeInMinutes AS totalFlightTime,
                           fromAirport.code AS fromAirport, fromAirport.name AS fromAirportName,
                           toAirport.code AS toAirport, toAirport.name AS toAirportName,
                           layoverAirport.code AS layoverAirport, layoverAirport.name AS layoverAirportName
                    """,
                    fromCity=fromCity, toCity=toCity
                )

                for record in layover_flights:
                    flight = {
                        "fromAirport": record["fromAirport"],
                        "toAirport": record["toAirport"],
                        "flights": [record["firstFlightNumber"], record["secondFlightNumber"]],
                        "price": record["price"],
                        "flightTimeInMinutes": record["totalFlightTime"],
                        "layoverAirport": record["layoverAirportName"]
                    }
                    flights.append(flight)

            if flights:
                return jsonify({"flights": flights}), 200
            else:
                return jsonify({"error": "Flights not found"}), 404
    except exceptions.Neo4jError as e:
        return jsonify({"error": "Failed to search flights", "details": str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            return jsonify({"message": "Database cleanup completed successfully."}), 200
    except exceptions.Neo4jError as e:
        # Jei ryšys nepavyksta, grąžiname aiškų pranešimą apie klaidą
        return jsonify({"error": "Failed to clean database", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)