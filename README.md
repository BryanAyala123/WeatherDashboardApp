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
- Health Check | /api/health | GET
- Create User | /api/create-user | PUT
- Login | /api/login | POST
- Logout | /api/logout | POST
- Change Password | /api/change-password | POST
- Reset Users | /api/reset-users | DELETE
- Reset Locations | api/reset-locations | DELETE
- Get Location By ID | /api/get-locatio-by-id/<int:location_id> | GET
- Get Weather History | /api/get-weather-from-location-history/<string:city_name>/<int:latitude>/<int:longitude> | GET
- Clear Favorites List | /api/clear-favorites | POST
- Get all Favorite Location | get_all_locations_from_favorite | GET
- Get Weather from Favorite location | /api/get-weather-from-favorite | POST



● A description of each route (example on ed discussion):

○ Route Name and Path
○ Request Type
■ GET, POST, PUT, DELETE
○ Purpose
○ Request Format
■ GET parameters
■ POST / PUT / DELETE body
○ Response Format
■ JSON keys and value types
○ Example
■ Request in the form of JSON body or cURL
command
■ Associated JSON response

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




