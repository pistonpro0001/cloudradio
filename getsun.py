import geocoder
from suntime import Sun, SunTimeException

g = geocoder.ip('me')

if g.latlng:
    lat, lon = g.latlng
else:
    raise ImportError("failed to get latitude and longitude of current IP")

sun = Sun(lat, lon)

# Test it
try:
    sun.get_sunrise_time()
    sun.get_sunset_time()
except SunTimeException as e:
    raise ImportError(e)

def sunrise():
    return sun.get_sunrise_time()

def sunset():
    return sun.get_sunset_time()

if __name__ == "__main__":
    print(sunrise(), sunset())