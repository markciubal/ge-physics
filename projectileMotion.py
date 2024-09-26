import simplekml
import math
from datetime import datetime, timedelta
import random

# Constants
DEFAULT_ICON = "http://maps.google.com/mapfiles/kml/shapes/donut.png"
GRAVITY_CONSTANT = 9.80  # Acceleration due to gravity (m/s^2)
DEGREE_OF_RADIUS_LINE = 111139  # Meters per degree latitude

def interpolate_times(start_time, end_time, intervals):
    """
    Interpolates a list of datetime objects between start_time and end_time.
    
    Parameters:
    - start_time: The starting datetime.
    - end_time: The ending datetime.
    - intervals: The number of intervals to divide the time range.

    Returns:
    - List of datetime objects interpolated between start_time and end_time.
    """
    delta = (end_time - start_time) / intervals
    # print([start_time + i * delta for i in range(intervals + 1)])
    return [start_time + i * delta for i in range(intervals + 1)]

def meters_to_lat_change(meters):
    """Converts meters to a change in latitude in degrees."""
    return meters / DEGREE_OF_RADIUS_LINE

def meters_to_long_change(meters, lat):
    """Converts meters to a change in longitude in degrees at a given latitude."""
    return meters / (DEGREE_OF_RADIUS_LINE * math.cos(math.radians(lat)))

def create_vector(kml, name, lat, lon, delta_i, delta_j, h1=0, h2=0, start_time=None, end_time=None):
    """
    Creates a vector in KML from a starting point to an end point defined by delta_i and delta_j, with optional time span.
    """
    delta_lat = meters_to_lat_change(delta_j)
    delta_lon = meters_to_long_change(delta_i, lat)
    end_lat = lat + delta_lat
    end_lon = lon + delta_lon

    linestring = kml.newlinestring(name=name)
    linestring.coords = [(lon, lat, h1), (end_lon, end_lat, h2)]
    linestring.style.labelstyle.scale = 0.6
    linestring.style.iconstyle.icon.href = DEFAULT_ICON
    linestring.style.iconstyle.scale = 0.5
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    
    if start_time and end_time:
        linestring.timespan.begin = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        linestring.timespan.end = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return end_lat, end_lon, h2

def create_vectors(kml, vectors, start_time=None, end_time=None):
    """
    Creates multiple vectors in KML with optional time span for each vector.
    """
    for vector in vectors:
        create_vector(
            kml,
            name=vector['name'],
            lat=vector['lat'],
            lon=vector['lon'],
            delta_i=vector['i'],
            delta_j=vector['j'],
            h1=vector.get('h1', 0),
            h2=vector.get('h2', 0),
            start_time=start_time,
            end_time=end_time
        )

def simulate_freefall(lat, lon, height, duration, intervals, name, start_time=None, end_time=None):
    """
    Simulates free fall and generates a KML file of the trajectory with optional start and end time.
    """
    kml = simplekml.Kml()
    if not start_time:
        start_time = datetime.utcnow()
    if not end_time:
        end_time = start_time + timedelta(seconds=duration)
    
    times = [start_time + timedelta(seconds=duration * i / intervals) for i in range(intervals + 1)]

    for t in times:
        elapsed_time = (t - start_time).total_seconds()
        h = height - 0.5 * GRAVITY_CONSTANT * elapsed_time**2
        if h < 0:
            h = 0
            break

        point = kml.newpoint()
        point.name = f"h: {h:.2f}m"
        point.coords = [(lon, lat, h)]
        point.style.labelstyle.scale = 0.6
        point.style.iconstyle.icon.href = DEFAULT_ICON
        point.style.iconstyle.scale = 0.5
        point.altitudemode = simplekml.AltitudeMode.relativetoground
        point.timestamp.when = t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    kml.save(f"{name}.kml")

def simulate_projectile_motion(lat, lon, h0, v0, elevation_angle_deg, azimuth_angle_deg, duration, intervals, name, start_time=None, end_time=None):
    """
    Simulates projectile motion and generates a KML file of the trajectory with optional time span.
    
    Parameters:
    - lat, lon: Initial latitude and longitude.
    - h0: Initial height in meters.
    - v0: Initial velocity in meters per second.
    - elevation_angle_deg: Launch elevation angle in degrees (0 = horizontal, 90 = vertical).
    - azimuth_angle_deg: Launch azimuth angle in degrees from north (0 = north, 90 = east).
    - duration: Total simulation duration in seconds.
    - intervals: Number of intervals to divide the simulation time.
    - name: Name of the KML file to be saved.
    - start_time: Optional start datetime (UTC).
    - end_time: Optional end datetime (UTC).
    """
    kml = simplekml.Kml()
    elevation_angle_rad = math.radians(elevation_angle_deg)
    azimuth_angle_rad = math.radians(azimuth_angle_deg)

    v0h = v0 * math.cos(elevation_angle_rad)  # Horizontal component
    v0v = v0 * math.sin(elevation_angle_rad)  # Vertical component

    v0x = v0h * math.sin(azimuth_angle_rad)  # East-West component (x)
    v0y = v0h * math.cos(azimuth_angle_rad)  # North-South component (y)

    if not start_time:
        start_time = datetime.utcnow()
    if not end_time:
        end_time = start_time + timedelta(seconds=duration)

    # Generate the interpolated times
    interpolated_times = interpolate_times(start_time, end_time, intervals)

    positions = []
    for idx, t in enumerate(interpolated_times):
        time_elapsed = idx * duration / intervals
        x = v0x * time_elapsed  # East-West displacement in meters
        y = v0y * time_elapsed  # North-South displacement in meters
        z = v0v * time_elapsed - 0.5 * GRAVITY_CONSTANT * time_elapsed**2  # Vertical displacement in meters
        h = h0 + z
        if h < 0:
            h = 0
            break

        delta_lat = meters_to_lat_change(y)
        delta_lon = meters_to_long_change(x, lat)

        current_lat = lat + delta_lat
        current_lon = lon + delta_lon

        # Add position and timestamp to the positions list
        positions.append((current_lon, current_lat, h))

        # Create point with timestamp
        point = kml.newpoint()
        point.coords = [(current_lon, current_lat, h)]
        point.timestamp.when = t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        point.altitudemode = simplekml.AltitudeMode.relativetoground

    # Create a KML line for the projectile path
    linestring = kml.newlinestring(name=name)
    linestring.coords = positions
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    linestring.style.linestyle.color = simplekml.Color.red
    linestring.style.linestyle.width = 3

    # Set the timespan for the entire line
    linestring.timespan.begin = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    linestring.timespan.end = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    kml.save(f"{name}.kml")

def create_circle(kml, latitude, longitude, altitude, radius, num_points, start_time=None, end_time=None):
    """
    Creates a circle polygon in KML with optional start and end time.
    """
    pol = kml.newpolygon(name="Circle")
    pol.extrude = 0
    pol.altitudemode = simplekml.AltitudeMode.relativetoground

    pol.style.polystyle.color = simplekml.Color.changealphaint(150, simplekml.Color.red)
    pol.style.linestyle.color = simplekml.Color.blue
    pol.style.linestyle.width = 2

    coords = []
    for i in range(num_points + 1):
        angle = math.radians(float(i) / num_points * 360)
        delta_lat = meters_to_lat_change(radius * math.cos(angle))
        delta_lon = meters_to_long_change(radius * math.sin(angle), latitude)
        coords.append((longitude + delta_lon, latitude + delta_lat, altitude))

    pol.outerboundaryis.coords = coords

    if start_time and end_time:
        pol.timespan.begin = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        pol.timespan.end = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def main():
    # Define the parameters
    start_lat = 38.662463
    start_lon = -121.125643
    circle_altitude = 100  # Altitude in meters
    circle_radius = 100  # Radius in meters
    points_on_circle = 36  # Number of segments
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(seconds=10)

    # Generate a circle KML with time span
    kml_circle = simplekml.Kml()
    create_circle(kml_circle, start_lat, start_lon, circle_altitude, circle_radius, points_on_circle, start_time, end_time)
    kml_circle.save("circle.kml")

    # Simulate free fall with time span
    simulate_freefall(start_lat, start_lon, height=100, duration=10000, intervals=10000, name="freefall", start_time=start_time, end_time=end_time)

    # Simulate projectile motion with time span
    simulate_projectile_motion(
        lat=start_lat,
        lon=start_lon,
        h0=0,
        v0=100,  # Initial speed in m/s
        elevation_angle_deg=45,  # Elevation angle
        azimuth_angle_deg=90,  # Azimuth angle (east)
        duration=110,
        intervals=100,
        name="projectile_motion",
        start_time=start_time,
        end_time=end_time
    )

    # Create vectors with time span
    kml_vectors = simplekml.Kml()
    vectors = []
    current_lat = start_lat
    current_lon = start_lon
    current_h = 0

    for i in range(1, 6):
        delta_i = random.uniform(-100, 100)
        delta_j = random.uniform(-100, 100)
        delta_h = random.uniform(0, 50)
        vectors.append({
            'name': f"Vector {i}",
            'lat': current_lat,
            'lon': current_lon,
            'i': delta_i,
            'j': delta_j,
            'h1': current_h,
            'h2': current_h + delta_h
        })
        # Update current position
        delta_lat = meters_to_lat_change(delta_j)
        delta_lon = meters_to_long_change(delta_i, current_lat)
        current_lat += delta_lat
        current_lon += delta_lon
        current_h += delta_h

    create_vectors(kml_vectors, vectors, start_time=start_time, end_time=end_time)
    kml_vectors.save("vectors.kml")

if __name__ == "__main__":
    main()
