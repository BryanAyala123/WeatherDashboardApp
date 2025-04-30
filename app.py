from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import ProductionConfig

from weather.db import db
from weather.models.locations_model import Locations
from weather.models.favoriteslist_model import FavoriteslistModel
from weather.models.user_model import Users
from weather.utils.logger import configure_logger

load_dotenv()

def create_app(config_class=ProductionConfig):
    """Create a Flask application with the specified configuration.

    Args:
        config_class (Config): The configuration class to use.

    Returns:
        Flask app: The configured Flask application.

    """
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)


   # FavoritesModel = FavoritesModel()
    app.favorites_model = FavoriteslistModel()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)


    ##########################################################
    #
    # User Management
    #
    #########################################################
    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)
        
    ##########################################################
    #
    # Location
    #
    ##########################################################
    @app.route("/api/reset-locations", methods=['DELETE'])
    def reset_locations() -> Response:
        """Recreate the locations table to delete locations.

        Returns:
            JSON response indicating the success of recreating the locations table.

        Raises:
            500 error if there is an issue recreating the locations table.
        """
        try:
            app.logger.info("Received request to recreate Locations table")
            with app.app_context():
                Locations.__table__.drop(db.engine)
                Locations.__table__.create(db.engine)
            app.logger.info("Locations table recreated successfully")
            return make_response(jsonify({
                "status":"success",
                "message": f"Locations table recreated successfully"
            }),200)
        
        except Exception as e:
            app.logger.error(f"Locations table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    @app.route('/api/get-locatio-by-id/<int:location_id>', methods=['GET'])
    @login_required
    def get_location_by_id(location_id: int) -> Response:
        """Route to retrieve a location by its ID.

        Path Parameter:
            - location_id (int): The ID of the location.

        Returns:
            JSON response containing the location details.

        Raises:
            400 error if the location does not exist.
            500 error if there is an issue retrieving the location.

        """
        try:
            app.logger.info(f"Received request to retrieve location with ID {location_id}")

            loc = Locations.get_location_by_id(location_id)
            if not loc:
                app.logger.warning(f"Location with ID {location_id} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location with ID {location_id} not found"
                }), 400)

            app.logger.info(f"Successfully retrieved location: {loc.city_name} it is {loc.feels_like} (ID {loc.id})")

            return make_response(jsonify({
                "status": "success",
                "message": "location retrieved successfully",
                "location": loc
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve location by ID: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the location",
                "details": str(e)
            }), 500)
    
    @app.route('/api/get-weather-from-location-history/<string:city_name>/<int:latitude>/<int:longitude>', methods=['GET'])
    @login_required
    def get_weather_from_location_history(city_name: str, latitude: int, longitude: int) -> Response:
        """
        Get weather from location history using city name and coordinates.

        Args (via URL):
            city_name (str): The name of the city.
            latitude (int): The integer latitude of the location.
            longitude (int): The integer longitude of the location.

        Returns:
            JSON response with weather info or error message.
        """
        try:
            app.logger.info(f"Fetching weather for {city_name} at ({latitude}, {longitude})")

            loc = Locations.get_weather_from_history(city_name, latitude, longitude)
            if not loc:
                return make_response(jsonify({
                    "status": "error",
                    "message": f"No weather history found for '{city_name}' at ({latitude}, {longitude})"
                }), 404)

            return make_response(jsonify({
                "status": "success",
                "weather": loc
            }), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving weather history: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }), 500)

        
    @app.route('/api/clear-favorites', methods=['POST'])
    @login_required
    def clear_favorite() -> Response:
        """Route to clear the list of location from the favorites.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            500 error if there is an issue clearing location.

        """
        try:
            app.logger.info("Clearing all locations...")

            Locations.clear_favoriteslist()

            app.logger.info("Location cleared from favorites successfully.")
            return make_response(jsonify({
                "status": "success",
                "message": "Location have been cleared from favorites."
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to clear Location: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while clearing Location",
                "details": str(e)
            }), 500)

    ############################################################
    #
    # Favorite Location List
    #
    ############################################################
    @app.route('/api/get-all-locations-from-favorite', methods=['GET'])
    @login_required
    def get_all_locations_from_favorite() -> Response:
        """Retrieve all locations in the favorite.

        Returns:
            JSON response containing the list of favorite.

        Raises:
            500 error if there is an issue retrieving the favorites.

        """
        try:
            app.logger.info("Received request to retrieve all locations from the favorite.")

            loc = Locations.get_all_locations()

            app.logger.info(f"Successfully retrieved {len(loc)} locations from the favorites.")
            return make_response(jsonify({
                "status": "success",
                "songs": loc
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve locations from favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/get-weather-from-favorite', methods=['POST'])
    @login_required
    def add_weather_to_favorite() -> Response:
        '''Route to get weather from the the fav by compound key (city_name, lat, long).

        Expected JSON Input:
            - City Name (str): The city's name.
            - latitude (float): the latitude of the location
            - longitude (float): the longitude of the location 

        Returns:
            JSON response indicating success of the addition.

        Raises:
            400 error if required fields are missing or the location does not exist.
            500 error if there is an issue adding the location to the favorites.
        '''
        
        try:
            app.logger.info("Received request to get weather from favorites")

            data = request.get_json()
            required_fields = ["city_name", "latitude", "longitude"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            city = data["city_name"]
            lat = data["latitude"]

            try:
                long = int(data["longitude"])
            except ValueError:
                app.logger.warning(f"Invalid long format: {data['longitude']}")
                return make_response(jsonify({
                    "status": "error",
                    "message": "longitude must be a valid integer"
                }), 400)

            app.logger.info(f"Looking up location: {city} - {lat} ({long})")
            loc = Locations.get_current_weather(city,lat,long)

            if not loc:
                app.logger.warning(f"Location not found: {city} - {lat} ({long})")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location '{city}' by {lat} ({long}) not found in catalog"
                }), 400)

            Locations.add_location_to_favoriteslist(city,lat,long)
            app.logger.info(f"Successfully added location to favorites: {city} - {lat} ({long})")

            return make_response(jsonify({
                "status": "success",
                "message": f"Location '{city}' by {lat} ({long}) added to favorites"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add location to favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the location to the favorites",
                "details": str(e)
            }), 500)
        
        

    
    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host="0.0.0.0", port=5001)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")