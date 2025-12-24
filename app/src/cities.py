CITIES = [
     # Asia
    "Colombo","Kandy", "Jaffna", "Shanghai", "Mumbai", "Beijing",
    "Dhaka", "Osaka", "Karachi", "Istanbul", "Chongqing",
    "Manila", "Tianjin", "Bangalore", "Seoul", "Jakarta",
    "Chennai", "Bangkok", "Hyderabad", "Lahore", "Shenzhen",
    "Guangzhou", "Singapore", "Kuala Lumpur", "Hong Kong", "Baghdad",
    "Riyadh", "Tehran", "Dubai", "Ankara", "Jeddah",
    "Kolkata", "Ahmedabad", "Pune", "Taipei", "Hanoi",
    
    # North America
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington",
    "Boston", "Nashville", "Detroit", "Portland", "Las Vegas",
    "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque",
    "Tucson", "Fresno", "Sacramento", "Kansas City", "Mesa",
    "Atlanta", "Omaha", "Colorado Springs", "Raleigh", "Miami",
    "Cleveland", "Tulsa", "Oakland", "Minneapolis", "Wichita",
    "Arlington", "Vancouver", "Toronto", "Montreal", "Calgary",
    "Ottawa", "Edmonton", "Winnipeg", "Quebec City", "Hamilton",
    
    # South America
    "São Paulo", "Rio de Janeiro", "Buenos Aires", "Lima", "Bogotá",
    "Santiago", "Caracas", "Brasília", "Fortaleza", "Guayaquil",
    "Quito", "La Paz", "Montevideo", "Asunción", "Medellín",
    
    # Europe
    "London", "Paris", "Berlin", "Madrid", "Rome",
    "Barcelona", "Vienna", "Amsterdam", "Brussels", "Stockholm",
    "Copenhagen", "Oslo", "Helsinki", "Prague", "Budapest",
    "Warsaw", "Bucharest", "Sofia", "Athens", "Lisbon",
    "Dublin", "Munich", "Hamburg", "Frankfurt", "Cologne",
    "Manchester", "Birmingham", "Milan", "Naples", "Turin",
    
    # Africa
    "Cairo", "Lagos", "Kinshasa", "Johannesburg", "Nairobi",
    "Khartoum", "Dar es Salaam", "Abidjan", "Alexandria", "Casablanca",
    "Algiers", "Cape Town", "Durban", "Addis Ababa", "Accra",
    
    # Australia & Oceania
    "Sydney", "Melbourne", "Brisbane", "Perth", "Auckland",
    "Adelaide", "Gold Coast", "Canberra", "Wellington",
]

def get_cities():
    """Return the list of cities."""
    return CITIES

def get_city_count():
    """Return the total number of cities."""
    return len(CITIES)
