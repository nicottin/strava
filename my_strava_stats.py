# pylint: disable=no-member
from pystrava import Strava
import datetime
import configparser

# Configutation input
config = configparser.RawConfigParser()
config.read('config.properties')
config_dict = dict(config.items('CONFIG'))

goal = float(config_dict["goal"])

def getActivities(start, end, full=False):
    activities = client.get_activities(before=end, after=start)
    total_distance = 0.0
    count = 0
    elevation = 0.0
    moving_time = 0
    gears = {}
    act_types = {}
    
    for act in activities:
        if act.type in ["Ride", "VirtualRide"]:
            count += 1
            total_distance += float(act.distance)
            elevation += float(act.total_elevation_gain)
            moving_time += act.moving_time.total_seconds()

            if act.gear_id in gears:
                gears[act.gear_id]["count"] += 1
                gears[act.gear_id]["elevation"] += float(act.total_elevation_gain)
                gears[act.gear_id]["distance"] += float(act.distance)
                gears[act.gear_id]["moving_time"] += act.moving_time.total_seconds()
            else:
                gears[act.gear_id] = {
                    "count": 1, 
                    "elevation": float(act.total_elevation_gain), 
                    "distance": float(act.distance), 
                    "moving_time": act.moving_time.total_seconds()
                }
            
            if act.type in act_types:
                act_types[act.type]["count"] += 1
                act_types[act.type]["elevation"] += float(act.total_elevation_gain)
                act_types[act.type]["distance"] += float(act.distance)
                act_types[act.type]["moving_time"] += act.moving_time.total_seconds()
            else:
                act_types[act.type] = {
                    "count": 1, 
                    "elevation": float(act.total_elevation_gain), 
                    "distance": float(act.distance), 
                    "moving_time": act.moving_time.total_seconds()
                }

    total_distance = total_distance / 1000
    virtual_distance = act_types["VirtualRide"]["distance"] / 1000 if "VirtualRide" in act_types else 0
    print(f"Total distance: {int(round(total_distance,0))} km ({int(round(virtual_distance/total_distance*100,0))}% virtual)")
    
    virtual_elevation = act_types["VirtualRide"]["elevation"]  if "VirtualRide" in act_types else 0
    print(f"Elevation: {int(round(elevation,0))} m ({int(round(virtual_elevation / elevation * 100, 0))}% virtual)")
    if moving_time > 0:
        print(f"Average speed: {round(total_distance/(moving_time/3600),2)} km/h")
    
    count_virtual = act_types["VirtualRide"]["count"] if "VirtualRide" in act_types else 0
    print(f"Activity count: {count} ({round(count_virtual / count * 100,  0)}% virtual)")

    day_of_year = datetime.datetime.now().timetuple().tm_yday
    diff = total_distance - goal if full else total_distance - (goal / 365 * day_of_year)
    sign = "+" if diff > 0 else ""
    print(f"Objective progress: {int(round(total_distance/goal*100,0))}% ({sign}{int(round(diff,0))} km)")
    
    if len(gears) > 1:
        for bike in gears:
            bike_details = client.get_gear(bike)
            print(f"\n\t{bike_details.name}")
            distance = gears[bike]["distance"] / 1000
            print(f"\t\tDistance: {int(round(distance,0))} km")
            print(f"\t\tElevation: {int(round(gears[bike]['elevation'],0))} m")
            if gears[bike]["moving_time"] > 0:
                print(f"\t\tAverage speed: {round(distance/(gears[bike]['moving_time']/3600),2)} km/h")
            
            print(f"\t\tActivity count: {gears[bike]['count']}")
        
        
    return

def getStatFullYear(years):
    for year in years:
        start = datetime.datetime.strptime(str(year), '%Y')
        end = datetime.datetime.strptime(str(int(year) + 1), '%Y')
        print(f"\nYear {year}")
        print("---------------------------------")
        getActivities(start, end, full=True)
    return

def getYearOverYear(years):
    for year in years:
        start = datetime.datetime.strptime(str(year), '%Y')
        today = datetime.datetime.today() + datetime.timedelta(days=1)
        month_day = datetime.datetime.strftime(today, "%m-%d")
        end = datetime.datetime.strptime(f"{year}-{month_day}", '%Y-%m-%d')
        print(f"\nYear to date {year}")
        print("---------------------------------")
        getActivities(start, end)
        print("\n")
    return


if __name__ == "__main__":

    config.read('.credentials.properties')
    cred_dict = dict(config.items('CREDENTIALS'))

    client = Strava(client_id=cred_dict["client_id"],
                    client_secret=cred_dict["client_secret"],
                    callback=cred_dict["callback"],
                    scope="activity:read_all,profile:read_all",
                    email=cred_dict["user"],
                    password=cred_dict["password"])

    now = datetime.datetime.now()
    current_year = now.year
    year_list = list(reversed(range(int(config_dict["year_start"]), current_year + 1)))
    getYearOverYear(year_list)
    print("\n#######################################################################\n")
    getStatFullYear(year_list)
