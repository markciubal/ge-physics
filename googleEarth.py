import simplekml
from datetime import datetime, timedelta
import time
import random
import math
from math import pi, cos, sin, radians

import sys
sys.path.append('../')
# We should implement this somewhere: https://geodesy.noaa.gov/api/gravd/gp?lat=40.0&lon=-80.0&eht=100.0
# This is the gravity API. It returns the gravity at a given lat, long, and height. We can use this to get the gravity constant for a given location.
default_icon = "http://maps.google.com/mapfiles/kml/shapes/donut.png"
GRAVITY_CONSTANT = 9.80
DEGREE_OF_RADIUS_LINE = 111139

def meters_to_lat_change(meters):
    """Converts meters to a change in latitude in degrees."""
    return meters / DEGREE_OF_RADIUS_LINE

def meters_to_long_change(meters, lat):
    """Converts meters to a change in longitude in degrees, given a latitude."""
    return meters / (DEGREE_OF_RADIUS_LINE * math.cos(math.radians(lat)))


class Particle:
    def vector_operations(vectors):
        kml = simplekml.Kml()
        results = []  # To store the final coordinates and k values for each vector
        for vector in vectors:
            name = vector['name']
            lat = vector['lat']
            long = vector['long']
            i = vector['i']
            j = vector['j']
            h1 = vector.get('h1', 0)  # Default value if h1 is not provided
            h2 = vector.get('h2', 0)  # Default value if h2 is not provided

            
            point = kml.newlinestring()
            point.name = name
            delta_lat = meters_to_lat_change(i)
            delta_long = meters_to_long_change(j, lat)
            print(f"{lat + delta_lat}, {long + delta_long}")
            point.coords = [(long, lat, h1), (long + delta_long, lat + delta_lat, h2)]
            point.style.labelstyle.scale = 0.6
            # Assuming 'default_icon' is defined somewhere globally
            point.style.iconstyle.icon.href = default_icon
            point.style.iconstyle.scale = 0.5
            point.altitudemode = simplekml.AltitudeMode.relativetoground
           

            results.append((lat + delta_lat, long + delta_long, h1, h2))
        kml.save(f"vector_operations.kml")
        return results
    def vector(name, lat, long, i, j, h1=0, h2=0):
        kml = simplekml.Kml()
        point = kml.newlinestring()
        point.name = name
        delta_lat = meters_to_lat_change(i)
        delta_long = meters_to_long_change(j, lat)
        print(str(lat + delta_lat) + ", " + str(long + delta_long))
        point.coords = [(long, lat, h1), (long + delta_long, lat + delta_lat, h2)]
        point.style.labelstyle.scale = 0.6
        point.style.iconstyle.icon.href = default_icon
        point.style.iconstyle.scale = 0.5
        point.altitudemode = simplekml.AltitudeMode.relativetoground
        # kml.save(f"{name}.kml")
        # Need to implement recursion for vectors, pass an array of matrices and use recursion to get a resultant KML. This is just a placeholder.
        return lat + delta_lat, long + delta_long, i, j, h1, h2

    def freefall(lat, long, height, name, duration, intervals=100):
        kml = simplekml.Kml()
        start_time = datetime.utcnow()
        previous_time = None
        previous_keight = None
        velocity = 0
        # Split the freefall into intervals
        for i in range(intervals + 1):
            fraction = i / intervals
            current_time = start_time + timedelta(seconds=duration * fraction)
            current_keight = height - ((1/2) * GRAVITY_CONSTANT * (duration * fraction)**2)  # Simple linear interpolation
            # if (current_keight < 0):
            #     current_keight = 0
            #     return
            # Create a new point for each interval
            # Calculate velocity
            if previous_time and previous_keight:
                velocity = (current_keight - previous_keight) / (current_time - previous_time).total_seconds()
            point = kml.newpoint()
            point.name = f"h: {current_keight:.2f}m, v: {velocity:.2f} m/s"
            point.coords = [(long, lat, current_keight)]
            point.style.labelstyle.scale = 0.6
            point.style.iconstyle.icon.href = default_icon
            point.style.iconstyle.scale = 0.5
            point.altitudemode = simplekml.AltitudeMode.relativetoground
            # point.timestamp.begin = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            point.timestamp.when = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            previous_time = current_time
            previous_keight = current_keight
        kml.save(f"freefall_{name}.kml")

    def horizontal_projection(lat, long, height, name, duration):
        kml = simplekml.Kml()
        newPoint = kml.newpoint(name=name)
        newPoint.coords = [(lat, long, height)]
        newPoint.altitudemode = simplekml.AltitudeMode.relativetoground
         # Get current UTC time
        start_time = datetime.utcnow()
        # Calculate end time by adding duration
        end_time = start_time + timedelta(seconds=duration)

        # Format times into strings
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Use TimeSpan for duration instead of TimeStamp
        newPoint.timespan.begin = start_time_str
        newPoint.timespan.end = end_time_str
        kml.save("horizontal_projection_" + name + ".kml")
def create_circle(latitude, longitude, altitude, radius, num_points, start_time, end_time):
    kml = simplekml.Kml()
    pol = kml.newpolygon(name="Circle")
    pol.extrude = 0
    pol.altitudemode = simplekml.AltitudeMode.relativetoground
    # Style
    polstyle = simplekml.PolyStyle(color=simplekml.Color.red, fill=1, outline=1)
    linestyle = simplekml.LineStyle(color=simplekml.Color.blue, width=5)
    pol.style.polystyle = polstyle
    pol.style.linestyle = linestyle

    # Time span
    pol.timespan.begin = start_time  # Start time in YYYY-MM-DD format
    pol.timespan.end = end_time  # End time in YYYY-MM-DD format
    # Generate the points on the circle and automatically include the first point at the end to close the circle
    coords = [(longitude + (cos(radians(angle_deg)) * radius / 111319.5),
               latitude + (sin(radians(angle_deg)) * radius * math.cos(radians(latitude)) / 111319.5),
               altitude) for angle_deg in (i * 360 / num_points for i in range(num_points + 1))]  # +1 to close the circle

    # Assign the points to the polygon's outer boundary
    pol.outerboundaryis.coords = coords

    return kml

def create_timed_segments_circle(latitude, longitude, altitude, radius, num_points, start_time, end_time):
    kml = simplekml.Kml()
    total_days = (end_time - start_time).days
    segment_days = total_days / num_points

    for i in range(num_points):
        # Calculate start and end times for this segment
        segment_start_time = start_time + timedelta(days=i * segment_days)
        segment_end_time = segment_start_time + timedelta(days=segment_days)

        # Create a new polygon for each segment
        pol = kml.newpolygon(name=f"Segment {i+1}")
        pol.extrude = 0
        pol.altitudemode = simplekml.AltitudeMode.relativetoground
        pol.style.polystyle = simplekml.PolyStyle(color=simplekml.Color.changealphaint(150, simplekml.Color.red), fill=1, outline=1)
        pol.style.linestyle = simplekml.LineStyle(color=simplekml.Color.blue, width=2)
        pol.timespan.begin = segment_start_time.strftime('%Y-%m-%d')
        pol.timespan.end = segment_end_time.strftime('%Y-%m-%d')

        # Calculate the coordinates for this segment
        coords = []
        angle_step = 360 / num_points
        start_deg = i * angle_step
        end_deg = (i + 1) * angle_step
        coords.append((longitude, latitude, altitude))  # Center point
        for angle_deg in [start_deg, end_deg]:
            angle_rad = radians(angle_deg)
            lon = longitude + (cos(angle_rad) * radius / 111319.5)
            lat = latitude + (sin(angle_rad) * radius * math.cos(radians(latitude)) / 111319.5)
            coords.append((lon, lat, altitude))

        coords.append((longitude, latitude, altitude))  # Close back to center
        pol.outerboundaryis.coords = coords

    return kml
 

def create_timed_segments_circle(latitude, longitude, altitude, radius, num_points, start_time, end_time):
    kml = simplekml.Kml()
    total_days = (end_time - start_time).days
    segment_days = total_days / num_points

    for i in range(num_points):
        # Calculate start and end times for this segment
        segment_start_time = start_time + timedelta(days=i * segment_days)
        segment_end_time = segment_start_time + timedelta(days=segment_days)

        # Create a new polygon for each segment
        pol = kml.newpolygon(name=f"Segment {i+1}")
        pol.extrude = 0
        pol.altitudemode = simplekml.AltitudeMode.relativetoground
        pol.style.polystyle = simplekml.PolyStyle(color=simplekml.Color.changealphaint(150, simplekml.Color.red), fill=1, outline=1)
        pol.style.linestyle = simplekml.LineStyle(color=simplekml.Color.blue, width=2)
        pol.timespan.begin = segment_start_time.strftime('%Y-%m-%d')
        pol.timespan.end = segment_end_time.strftime('%Y-%m-%d')

        # Calculate the coordinates for this segment
        coords = []
        angle_step = 360 / num_points
        start_deg = i * angle_step
        end_deg = (i + 1) * angle_step
        coords.append((longitude, latitude, altitude))  # Center point
        vectors = []
        for angle_deg in [start_deg, end_deg]:
            angle_rad = radians(angle_deg)
            lon = longitude + (cos(angle_rad) * radius / 111319.5)
            lat = latitude + (sin(angle_rad) * radius * math.cos(radians(latitude)) / 111319.5)
            coords.append((lon, lat, altitude))

            # Create vectors radiating out from the center
            vector_line = kml.newlinestring(name=f"Vector from Segment {i+1} at {angle_deg} degrees")
            vector_line.timespan.begin = segment_start_time.strftime('%Y-%m-%d')
            vector_line.timespan.end = segment_end_time.strftime('%Y-%m-%d')
            vector_line.coords = [(longitude, latitude, altitude), (lon, lat, altitude)]
            pol.altitudemode = simplekml.AltitudeMode.relativetoground
            vector_line.style.linestyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
            vector_line.style.linestyle.width = 4

        coords.append((longitude, latitude, altitude))  # Close back to center
        pol.outerboundaryis.coords = coords

    return kml

# Define the parameters for the circle and time span
start_lat = 38.662463
start_long = -121.125643
circle_altitude = 100  # Altitude in meters
circle_radius = 100  # Radius in meters
points_on_circle = 36  # Number of segments
start_time = datetime(2024, 1, 1)
end_time = datetime(2025, 1, 1)

# Generate the KML
circle_kml = create_timed_segments_circle(start_lat, start_long, circle_altitude, circle_radius, points_on_circle, start_time, end_time)
circle_kml.save("timed_circle_segments.kml")
circle_kml = create_timed_segments_circle(start_lat, start_long, circle_altitude, circle_radius, points_on_circle, start_time, end_time)
circle_kml.save("timed_circle_with_vectors.kml")
# For some reason these are switched. x gives a change in the value of the longitude, and y gives a change in the value of the latitude.
i = 0
j = 0
# Path: googleEarth.py
Particle.freefall(start_lat, start_long, random.randrange(100)*random.randrange(-1, 1), "Group 8", 10, 100)
   # Generate the KML
circle_kml = create_circle(start_lat, start_long, circle_altitude, circle_radius, points_on_circle, start_time, end_time)
circle_kml.save("circle.kml")
# Need to implement recursion for vectors
while True: 
    vector_1_lat, vector_1_lon, vector_1_i, vector_1_j, vector_1_k1, vector_1_k2 = Particle.vector("Vector 1", start_lat, start_long, i, j, 0, 25)
    vector_2_lat, vector_2_lon, vector_2_i, vector_2_j, vector_2_k1, vector_2_k2 = Particle.vector("Vector 2", vector_1_lat, vector_1_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_1_k2, random.randrange(100))
    vector_3_lat, vector_3_lon, vector_3_i, vector_3_j, vector_3_k1, vector_3_k2 = Particle.vector("Vector 3", vector_2_lat, vector_2_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_2_k2, random.randrange(100))
    vector_4_lat, vector_4_lon, vector_4_i, vector_4_j, vector_4_k1, vector_4_k2 = Particle.vector("Vector 4", vector_3_lat, vector_3_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_3_k2, random.randrange(100))
    vector_5_lat, vector_5_lon, vector_5_i, vector_5_j, vector_5_k1, vector_5_k2 = Particle.vector("Vector 5", vector_4_lat, vector_4_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_4_k2, random.randrange(100))
    vector_6_lat, vector_6_lon, vector_6_i, vector_6_j, vector_6_k1, vector_6_k2 = Particle.vector("Vector 6", vector_5_lat, vector_5_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_5_k2, random.randrange(100))
    vector_7_lat, vector_7_lon, vector_7_i, vector_7_j, vector_7_k1, vector_7_k2 = Particle.vector("Vector 7", vector_6_lat, vector_6_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_6_k2, random.randrange(100))
    vector_8_lat, vector_8_lon, vector_8_i, vector_8_j, vector_8_k1, vector_8_k2 = Particle.vector("Vector 8", vector_7_lat, vector_7_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_7_k2, random.randrange(100))
    vector_9_lat, vector_9_lon, vector_9_i, vector_9_j, vector_9_k1, vector_9_k2 = Particle.vector("Vector 9", vector_8_lat, vector_8_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_8_k2, random.randrange(100))
    vector_10_lat, vector_10_lon, vector_10_i, vector_10_j, vector_10_k1, vector_10_k2 = Particle.vector("Vector 10", vector_9_lat, vector_9_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_9_k2, random.randrange(100))
    vector_11_lat, vector_11_lon, vector_11_i, vector_11_j, vector_11_k1, vector_11_k2 = Particle.vector("Vector 11", vector_10_lat, vector_10_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_10_k2, random.randrange(100))
    vector_12_lat, vector_12_lon, vector_12_i, vector_12_j, vector_12_k1, vector_12_k2 = Particle.vector("Vector 12", vector_11_lat, vector_11_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_11_k2, random.randrange(100))
    vector_13_lat, vector_13_lon, vector_13_i, vector_13_j, vector_13_k1, vector_13_k2 = Particle.vector("Vector 13", vector_12_lat, vector_12_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_12_k2, random.randrange(100))
    vector_14_lat, vector_14_lon, vector_14_i, vector_14_j, vector_14_k1, vector_14_k2 = Particle.vector("Vector 14", vector_13_lat, vector_13_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_13_k2, random.randrange(100))
    vector_15_lat, vector_15_lon, vector_15_i, vector_15_j, vector_15_k1, vector_15_k2 = Particle.vector("Vector 15", vector_14_lat, vector_14_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_14_k2, random.randrange(100))
    vector_16_lat, vector_16_lon, vector_16_i, vector_16_j, vector_16_k1, vector_16_k2 = Particle.vector("Vector 16", vector_15_lat, vector_15_lon, random.randrange(100)*random.randrange(-1, 1), random.randrange(100)*random.randrange(-1, 1), vector_15_k2, random.randrange(100))



    # Particle.horizontal_projectioan(38.66226127273164, -121.1262282178109, 10, "Group 8", 10)
    vectors = [
        {"name": "Vector 1", "lat": start_lat, "long": start_long, "i": vector_1_i, "j": vector_1_j, "h1": 0, "h2": 25},
        {"name": "Vector 2", "lat": vector_1_lat, "long": vector_1_lon, "i": vector_2_i, "j": vector_2_j, "h1": vector_1_k2, "h2": vector_2_k2},
        {"name": "Vector 3", "lat": vector_2_lat, "long": vector_2_lon, "i": vector_3_i, "j": vector_3_j, "h1": vector_2_k2, "h2": vector_3_k2},
        {"name": "Vector 4", "lat": vector_3_lat, "long": vector_3_lon, "i": vector_4_i, "j": vector_4_j, "h1": vector_3_k2, "h2": vector_4_k2},
        {"name": "Vector 5", "lat": vector_4_lat, "long": vector_4_lon, "i": vector_5_i, "j": vector_5_j, "h1": vector_4_k2, "h2": vector_5_k2},
        {"name": "Vector 6", "lat": vector_5_lat, "long": vector_5_lon, "i": vector_6_i, "j": vector_6_j, "h1": vector_5_k2, "h2": vector_6_k2},
        {"name": "Vector 7", "lat": vector_6_lat, "long": vector_6_lon, "i": vector_7_i, "j": vector_7_j, "h1": vector_6_k2, "h2": vector_7_k2},
        {"name": "Vector 8", "lat": vector_7_lat, "long": vector_7_lon, "i": vector_8_i, "j": vector_8_j, "h1": vector_7_k2, "h2": vector_8_k2},
        {"name": "Vector 9", "lat": vector_8_lat, "long": vector_8_lon, "i": vector_9_i, "j": vector_9_j, "h1": vector_8_k2, "h2": vector_9_k2},
        {"name": "Vector 10", "lat": vector_9_lat, "long": vector_9_lon, "i": vector_10_i, "j": vector_10_j, "h1": vector_9_k2, "h2": vector_10_k2},
        {"name": "Vector 11", "lat": vector_10_lat, "long": vector_10_lon, "i": vector_11_i, "j": vector_11_j, "h1": vector_10_k2, "h2": vector_11_k2},
        {"name": "Vector 12", "lat": vector_11_lat, "long": vector_11_lon, "i": vector_12_i, "j": vector_12_j, "h1": vector_11_k2, "h2": vector_12_k2},
        {"name": "Vector 13", "lat": vector_12_lat, "long": vector_12_lon, "i": vector_13_i, "j": vector_13_j, "h1": vector_12_k2, "h2": vector_13_k2},
        {"name": "Vector 14", "lat": vector_13_lat, "long": vector_13_lon, "i": vector_14_i, "j": vector_14_j, "h1": vector_13_k2, "h2": vector_14_k2},
        {"name": "Vector 15", "lat": vector_14_lat, "long": vector_14_lon, "i": vector_15_i, "j": vector_15_j, "h1": vector_14_k2, "h2": vector_15_k2},
        ]
    results = Particle.vector_operations(vectors)
    time.sleep(1)

