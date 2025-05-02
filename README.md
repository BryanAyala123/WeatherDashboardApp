# WeatherDashboardApp
## Overview
WeatherDashboardApp allows managing and displaying weather data from user favorite locations.

### Features 
- Allows users to set locations as a Favorite location 
- View current weather for all Favorite locations
- View all locations the user set as a favorite location
- Obtain historical weather access (latest 3 weather reports per location)
- Get 5 day forecast for a Favorite location

### Route Documentation
Route: /health
- Request Type: GET
- Purpose:Verify the service is running
- Request Body:
  - no request body for this route
- Response Format: JSON 
  - Success Response Example:
    - Code: 200
    - Content:{ 'status': 'success', 'message': 'Service is running' }
- Example Request:  curl -X GET http://localhost:5000/api/health
- Example Response: 
{
  "status": "success",
  "message": "Service is running"
}


Route: /create-user
- Request Type: PUT
- Purpose: Register a new user account
- Request Body:
  - username (str): The desired username
  - password (str): The desired password.
- Response Format: JSON
  - Success Response Example:
    - Code: 201 
    - Content: {"status": "success",
                "message": f"User '{username}' created successfully"}
- Example Request: curl -X PUT http://localhost:5000/api/create-user \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"s3cret"}'
- Example Response:
{
  "status": "success",
  "message": "User 'alice' created successfully"
}

Route: /login
- Request Type: POST
- Purpose: Authenticate a user and log them in
- Request Body:
  - username (str): The username of the user.
  - password (str): The password of the user.
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {"status": "success",
                    "message": f"User '{username}' logged in successfully"}
- Example Request: curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"s3cret"}'
- Example Response: 
{
  "status": "success",
  "message": "User 'alice' logged in successfully"
}


Route: /logout
- Request Type: POST
- Purpose: Log out the current user
- Request Body:
  - no request body for this route
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {"status": "success", "message": "User logged out successfully"}
- Example Request: curl -X POST http://localhost:5000/api/logout \
     --cookie "session=<your-session-cookie>"
- Example Response: 
{
  "status": "success",
  "message": "User logged out successfully"
}


Route: /change-password
- Request Type: POST
- Purpose: Change the password for the current user
- Request Body:
  - new_password (str): The new password to set.
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {
                "status": "success", "message": "Password changed successfully"}
- Example Request: curl -X POST http://localhost:5000/api/change-password \
     -H "Content-Type: application/json" \
     --cookie "session=<your-session-cookie>" \
     -d '{"new_password":"n3wp@ss"}'
- Example Response: 
{
  "status": "success",
  "message": "Password changed successfully"
}


Route: /reset-users 
- Request Type: DELETE
- Purpose: Recreate the users table to delete all users
- Request Body:
  - no request body for this route
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {"status": "success","message": f"Users table recreated successfully"}
- Example Request: curl -X DELETE http://localhost:5000/api/reset-users
- Example Response: 
{
  "status": "success",
  "message": "Users table recreated successfully"
}


Route: /reset-locations 
- Request Type: DELETE
- Purpose: Recreate the locations table to delete locations
- Request Body:
  - no request body for this route
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {"status":"success", "message": f"Locations table recreated successfully"}
- Example Request: curl -X DELETE http://localhost:5000/api/reset-locations
- Example Response: 
{
  "status": "success",
  "message": "Locations table recreated successfully"
}


Route: /get-location-by-id/<int:location_id>
- Request Type: GET
- Purpose: retrieve a location by its ID.
- Request Body:
  - no request body for this route
- Response Format: JSON
  - Success Response Example:
    - Code: 200 
    - Content: {"status": "success", "message": "location retrieved successfully","location": loc}
- Example Request: curl -X GET http://localhost:5000/api/get-location-by-id/5 \
     --cookie "session=<your-session-cookie>"
- Example Response: 
{
  "status": "success",
  "message": "location retrieved successfully",
  "location": {
    "id": 5,
    "city_name": "Boston",
    "latitude": 42.36,
    "longitude": -71.06
  }
}


Route: /get-weather-from-location-history/<string:city_name>/<int:latitude>/<int:longitude>
- Request Type: GET
- Purpose: Get weather from location history using city name and coordinates.
- Request Body:
  - no request body for this route
- Response Format: JSON
- Success Response Example:
    - Code: 200 
    - Content: {"status": "success", "weather": loc}
- Example Request: curl -X GET http://localhost:5000/api/get-weather-from-location-history/Boston/42.36/-71.06 \
     --cookie "session=<your-session-cookie>"
- Example Response: 
{
  "status": "success",
  "weather": {
    "id": 42,
    "city_name": "Boston",
    "latitude": 42.36,
    "longitude": -71.06,
    "temp": 15.2,
    "feels_like": 14.0,
    "pressure": 1013,
    "humidity": 60,
    "weather_main": "Clouds",
    "weather_description": "overcast clouds",
    "time": "2025-04-29T14:00:00"
  }
}


Route: /clear-favorites
- Request Type: POST
- Purpose: Clear the list of location from the favorites.
- Request Body:
  - no request body for this route
- Response Format: JSON
- Success Response Example:
    - Code: 200 
    - Content: {"status": "success","message": "Location have been cleared from favorites."}
- Example Request: curl -X POST http://localhost:5000/api/clear-favorites \
     --cookie "session=<your-session-cookie>"
- Example Response: 
{
  "status": "success",
  "message": "Location have been cleared from favorites."
}


Route: /get-all-locations-from-favorite
- Request Type: GET
- Purpose: Retrieve all locations in the favorite
- Request Body:
  - no request body for this route
- Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: {"status": "success","songs": loc}
- Example Request: curl -X GET http://localhost:5000/api/get-all-locations-from-favorite \
     --cookie "session=<your-session-cookie>"
- Example Response: 
{
  "status": "success",
  "songs": [
    ["Boston", 42.36, -71.06],
    ["Seattle", 47.61, -122.33]
  ]
}


Route: /get-weather-from-favorite
- Request Type: POST
- Purpose: Get weather from the the favorite location by compound key (city_name, lat, long)
- Request Body:
   - City Name (str): The city's name.
   - latitude (float): the latitude of the location
   - longitude (float): the longitude of the location 
- Response Format: JSON
  - Success Response Example:
    - Code: 201 
    - Content: {"status": "success","message": f"Location '{city}' by {lat} ({long}) added to favorites"}
- Example Request: curl -X POST http://localhost:5000/api/get-weather-from-favorite \
     -H "Content-Type: application/json" \
     --cookie "session=<your-session-cookie>" \
     -d '{"city_name":"Boston","latitude":42.36,"longitude":-71.06}'
- Example Response: 
{
  "status": "success",
  "message": "Location 'Boston' by 42.36 (-71.06) added to favorites"
}


Unit tests:
<pre>```
====================== test session starts ======================
platform darwin -- Python 3.9.10, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/aaronhuang/Desktop/WeatherDashboardApp
plugins: mock-3.14.0
collected 36 items                                              

tests/test_api_utils.py ........                          [ 22%]
tests/test_favoriteslist_model.py .........               [ 47%]
tests/test_locations_model.py ........                    [ 69%]
tests/test_user_model.py ...........                      [100%]

======================= warnings summary ========================
tests/test_locations_model.py::test_get_location_by_id
tests/test_locations_model.py::test_get_location_by_id_not_found
  /Users/aaronhuang/Desktop/WeatherDashboardApp/weather/models/locations_model.py:70: LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy and becomes a legacy construct in 2.0. The method is now available as Session.get() (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    location=cls.query.get(location_id)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================ 36 passed, 2 warnings in 1.61s =================
```</pre>
Smoketests:
<pre>
```
python smoketest.py
Reset users successful
Reset Location successful
User creation successful
Login successful
Password change successful
Login with new password successful
```
</pre>




