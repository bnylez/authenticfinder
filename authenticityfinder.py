import requests
import urllib.parse
import argparse

class UserInputs:
    """
    This class is responsible for capturing user inputs for the application.

    Attributes:
        startloc (str): Starting location input by the user.
        endloc (str): Ending location input by the user.
        keyword (str): Keyword for the search, input by the user.
        distoffpath (float): Maximum distance user is willing to deviate from the path, in miles.
    """
    def __init__(self):
        """
        Initializes the UserInputs class by prompting the user for input and setting the attributes.  
        """
        self.startloc = self.get_startloc()
        self.endloc = self.get_endloc()
        self.keyword = self.get_keyword()
        self.distoffpath = self.get_distoffpath()

    def get_startloc(self):
        """
        Prompts the user for the starting location.

        Returns:
            str: The starting location input by the user.
        """
        # You can use input() to get user input if this is a console application
        return input("Enter the starting location: ")

    def get_endloc(self):
        
        """
        Prompts the user for the ending location.

        Returns:
            str: The ending location input by the user.
        """
    
        return input("Enter the ending location: ")

    def get_keyword(self):
        """
        Prompts the user for a search keyword (e.g., 'antique stores', 'national parks').

        Returns:
            str: The search keyword input by the user.
        """
    
        return input("Enter the search keyword (e.g., 'antique stores', 'national parks'): ")

    def get_distoffpath(self):
        """
        Prompts the user for the maximum distance they are willing to deviate from the path.

        Returns:
            float: The maximum distance, in miles, input by the user.
        """

        return float(input("Enter the maximum distance willing to go off the path (in miles): "))

class Route:
    """
        Initializes the Route class with starting and ending locations.

        Args:
            startloc (str): The starting location for the route.
            endloc (str): The ending location for the route.
    """
    def __init__(self, startloc, endloc):
        """
        Fetches the route data from the Google Maps API.

        Args:
            api_key (str): The API key for accessing the Google Maps API.

        Returns:
            dict: The route data in JSON format.
        """
        self.startloc = startloc
        self.endloc = endloc
        self.waypoints = []

    def fetch_route(self, api_key):  # Changed to instance method, removed start, end as they are instance attributes
        """
        Fetches the route data from the Google Maps API.

        Args:
            api_key (str): The API key for accessing the Google Maps API.

        Returns:
            dict: The route data in JSON format.
        """
    
        encoded_start = urllib.parse.quote(self.startloc)
        encoded_end = urllib.parse.quote(self.endloc)
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={encoded_start}&destination={encoded_end}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching route: {response.status_code}")
            return None

    def calculate_waypoints(self, route, interval_miles):  # Changed to instance method
        """
        Calculates waypoints along the route at specified intervals.

        Args:
            route (dict): The route data.
            interval_miles (float): The interval, in miles, at which to calculate waypoints.

        Modifies:
            self.waypoints: Populates this list with the calculated waypoints.
        """

        self.waypoints = []  # Reset waypoints
        accumulated_distance = 0  # Distance accumulated over steps

        for leg in route['routes'][0]['legs']:
            for step in leg['steps']:
                step_distance = step['distance']['value'] / 1609.34  # Convert meters to miles
                accumulated_distance += step_distance

                if accumulated_distance >= interval_miles:
                    self.waypoints.append((step['end_location']['lat'], step['end_location']['lng']))
                    accumulated_distance -= interval_miles  # Decrement for next waypoint

class POIloc:
    """
    This class is responsible for finding points of interest (POIs) near the route.

    Attributes:
        waypoints (list): The waypoints along the route.
        api_key (str): The API key for accessing the Google Maps API.
        keyword (str): The search keyword for the points of interest.
        distoffpath (float): The maximum distance, in meters, from the path to search for POIs.
    """
    
    def __init__(self, waypoints, api_key, keyword, distoffpath):
        """
        Initializes the POIloc class with waypoints, API key, search keyword, and distance off path.

        Args:
            waypoints (list): The waypoints along the route.
            api_key (str): The API key for accessing the Google Maps API.
            keyword (str): The search keyword for the points of interest.
            distoffpath (float): The maximum distance, in meters, from the path to search for POIs.
        """
        self.waypoints = waypoints
        self.api_key = api_key
        self.keyword = keyword
        self.distoffpath = distoffpath  # distance in meters

    def search_nearby(self, location):
        """
        Searches for nearby points of interest based on a location.

        Args:
            location (tuple): The latitude and longitude of the location to search near.

        Returns:
            list: A list of points of interest near the specified location.
        """
        
        base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{location[0]},{location[1]}",
            'radius': self.distoffpath,
            'keyword': self.keyword,
            'key': self.api_key
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()['results']
        else:
            print(f"Error fetching POIs: {response.status_code}")
            return []

    def search_waypoints(self):
        """
        Searches for points of interest near all the waypoints.

        Returns:
            list: A list of points of interest near the waypoints.
        """
        poi_results = []
        for waypoint in self.waypoints:
            results = self.search_nearby(waypoint)
            poi_results.extend(results)
        return poi_results
        

# Your existing class definitions for UserInputs, Route, and POIloc go here.
def main(api_key, startloc=None, endloc=None, keyword=None, distoffpath=None):
    """
    The main function of the application, orchestrating the flow from user input to displaying POIs.

    Args:
        api_key (str): The API key for accessing the Google Maps API.
        startloc (str, optional): The starting location for the route.
        endloc (str, optional): The ending location for the route.
        keyword (str, optional): The search keyword for the points of interest.
        distoffpath (float, optional): The maximum distance, in miles, from the path to search for POIs.

    Side Effects:
        - Prompts
    """
    if not all([startloc, endloc, keyword, distoffpath]):
        user_inputs = UserInputs()
        startloc = user_inputs.startloc
        endloc = user_inputs.endloc
        keyword = user_inputs.keyword
        distoffpath = user_inputs.distoffpath

    else:
        distoffpath = float(distoffpath)

    # Instantiate Route and call its methods
    route = Route(startloc, endloc)  # Create an instance of Route
    route_data = route.fetch_route(api_key)  # Call instance method

    if not route_data:
        print("Failed to fetch route data.")
        return

    # Calculate waypoints using the route data
    route.calculate_waypoints(route_data, interval_miles=25)  # Call instance method

    # Create an instance of POIloc using the waypoints from the route instance
    poi_lookup = POIloc(route.waypoints, api_key, keyword, distoffpath * 1609.34)  # Convert miles to meters
    poi_results = poi_lookup.search_waypoints()

    # Output the results
    for poi in poi_results:
        print(poi.get('name', 'No name available'))  # Safely get the name or a default value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find POIs along a route.")
    parser.add_argument("--apikey", help="Google API key", required=True)
    parser.add_argument("--start", help="Starting location")
    parser.add_argument("--end", help="Ending location")
    parser.add_argument("--keyword", help="Search keyword (e.g., 'antique stores', 'national parks')")
    parser.add_argument("--distance", help="How far off the path are you willing to go?")

    args = parser.parse_args()
    
    main(args.apikey, args.start, args.end, args.keyword, args.distance)
