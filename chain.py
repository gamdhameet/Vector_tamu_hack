import requests
import json
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_place_id(bus_stop_name):
    """Convert a bus stop name to a Google Place ID."""
    places_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    places_api_key = ""
    params = {
        "input": bus_stop_name,
        "inputtype": "textquery",
        "fields": "place_id,name",
        "key": places_api_key
    }
    response = requests.get(places_url, params=params)
    data = response.json()
    if data["status"] == "OK":
        return data["candidates"][0]["place_id"]
    return None

def get_place_details(place_id):
    """Retrieve latitude, longitude, and address using a Place ID."""
    places_url = "https://maps.googleapis.com/maps/api/place/details/json"
    places_api_key = ""
    params = {
        "place_id": place_id,
        "key": places_api_key
    }
    response = requests.get(places_url, params=params)
    data = response.json()
    if data["status"] == "OK":
        result = data["result"]
        return {
            "name": result.get("name", "N/A"),
            "address": result.get("formatted_address", "N/A"),
            "lat": result.get("geometry", {}).get("location", {}).get("lat", "N/A"),
            "lng": result.get("geometry", {}).get("location", {}).get("lng", "N/A")
        }
    return None

def get_trip_details(origin, destination):
    """Fetch trip details based on place IDs."""
    origin_place_id = get_place_id(origin)
    destination_place_id = get_place_id(destination)
    
    if not origin_place_id or not destination_place_id:
        return None
    
    origin_details = get_place_details(origin_place_id)
    destination_details = get_place_details(destination_place_id)
    
    if not origin_details or not destination_details:
        return None

    current_time = int(time.time())
    payload = {
        "arriveTime": 0,
        "departTime": current_time,
        "destination": destination_details["name"],
        "destinationLatitude": destination_details["lat"],
        "destinationLongitude": destination_details["lng"],
        "destinationName1": destination_details["address"],
        "destinationName2": destination_details["name"],
        "origin": origin_details["name"],
        "originLatitude": origin_details["lat"],
        "originLongitude": origin_details["lng"],
        "originName1": origin_details["address"],
        "originName2": origin_details["name"],
        "routeOption": 0
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://aggiespirit.ts.tamu.edu/TripPlanner/Results?o1={origin}&opid={origin_place_id}&d1={destination}&dpid={destination_place_id}&dt=f{current_time}&ro=0",
        "Origin": "https://aggiespirit.ts.tamu.edu",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "RequestVerificationToken": "hytO9DbrTvKYvA4CepVzMvbUH1aF-iH5yfjX4ZqsiO63aCz4Wxo-rSRontHu0g4-BfuVl-JjrIKX86BGV6m0Op5_0-sCzTAqYiRP1X0WICU1:WUy-Y1hbEZPmHqHclA-97_S9jnzhHP_0Z3D_4k8udi-0Q9HIwqm00j0HkPqI3LHBwqx7LJbbSTMC7tFy2PdyScBw7BCRZkiArDzTlCk2mT41",
    }
    
    response = requests.post("https://aggiespirit.ts.tamu.edu/TripPlanner/GetTripPlan", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/trip', methods=['GET'])
def trip_plan():
    origin = request.args.get('origin')
    dest = request.args.get('dest')
    
    if not origin or not dest:
        return jsonify({"error": "Missing origin or destination parameter"}), 400
    
    trip_data = get_trip_details(origin, dest)
    
    if trip_data:
        return jsonify(trip_data)
    else:
        return jsonify({"error": "Failed to retrieve trip details"}), 500

if __name__ == '__main__':
    app.run(debug=True)