import random
import folium
import pandas

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def take_input():
    """
    Takes input from user and returns it if it fits and returns -1 otherwise
    """
    inp = input("Enter a year: ")
    try:
        inp = int(inp)
    except:
        print("The year should be represented as a number")
        return -1
    return inp


def generate_map(data, year):
    """
    Generates html code where map with locations from data is represented
    :param data: dict
    :param year: int
    :return: None
    """
    map = folium.Map()
    film_locations = folium.FeatureGroup(name="Film locations")
    population_layer = folium.FeatureGroup(name="Population")
    for counter, loc in enumerate(data.keys()):
        try:
            film = random.choice(data[loc][:-1])
            num_of_films = len(data[loc])-1
            if num_of_films > 1:
                popup = film + " and {} others".format(num_of_films-1)
            else:
                popup = film + " and 1 more"
                film_locations.add_child(folium.Marker(location=data[loc][-1],
                                        popup=popup))
            print(data[loc][-1])
        except Exception as err:
            print(err)
    add_population_layer(population_layer)
    map.add_child(film_locations)
    map.add_child(population_layer)
    map.add_child(folium.LayerControl())
    map.save("films_recorded_in_" + str(year) + ".html")


def get_dict_for_year(year, file_name="locations.csv"):
    """
    Reads file with filename and returns values extracted from it in dictionary
    :param year: int
    :param file_name: str
    :return: dict
    """
    res = dict()
    data = pandas.read_csv(file_name, error_bad_lines=False)
    for line, year_temp in enumerate(data['year']):
        if year_temp == str(year):
            location = data['location'][line]
            movie = data['movie'][line].strip()
            if location in res.keys():
                res[location].append(movie)
            else:
                res[location] = [movie]
    return res


def add_population_layer(map):
    """
    Adds population layer to map object given
    """
    fg_pp = folium.FeatureGroup(name="Population")

    fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
                                             encoding='utf-8-sig').read(),
                                   style_function=lambda x: {'fillColor': 'green'
                                   if x['properties']['POP2005'] < 10000000
                                   else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
                                   else 'red'}))
    map.add_child(fg_pp)


def add_coords(data):
    """
    Gets coordinates of locations which are keys for dict given and adds them to the end of key value
    """
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for location in data.keys():
        temp = location
        try:
            location = geolocator.geocode(location)
            if location:
                print(location)
                coords = [float(location.latitude), float(location.longitude)]
                data[temp].append(coords)
        except:
            pass
    return data


if __name__ == "__main__":
    year = take_input()
    if year != -1:

        data = add_coords(get_dict_for_year(year))
        generate_map(data, year)