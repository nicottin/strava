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
    
    for act in activities:
        if act.type in ["Ride", "VirtualRide"]:
            count += 1
            total_distance = total_distance + float(act.distance)
            elevation = elevation + float(act.total_elevation_gain)
            moving_time = moving_time + act.moving_time.total_seconds()

    total_distance = total_distance / 1000
    print("Total distance: {} km".format(int(round(total_distance,0))))
    print("Elevation: {} m".format(int(round(elevation,0))))
    if moving_time > 0:
        print("Average speed: {} km/h".format(round(total_distance/(moving_time/3600),2)))
    print("Activity count: {}".format(count))

    day_of_year = datetime.datetime.now().timetuple().tm_yday
    if full:
        diff = total_distance - goal 
    else:
        diff = total_distance - (goal / 365 * day_of_year)
    sign = ""
    if diff > 0:
        sign = "+"

    print("Objective progress: {}% ({}{} km)".format(int(round(total_distance/goal*100,0)),sign, int(round(diff,0))))
    return

def getStatFullYear(years):
    for year in years:
        start = datetime.datetime.strptime(str(year), '%Y')
        end = datetime.datetime.strptime(str(int(year) + 1), '%Y')
        print("\nYear {}".format(year))
        print("---------------------------------")
        getActivities(start, end, full=True)
    return

def getYearOverYear(years):
    for year in years:
        start = datetime.datetime.strptime(str(year), '%Y')
        today = datetime.datetime.today() + datetime.timedelta(days=1)
        month_day = datetime.datetime.strftime(today, "%m-%d")
        end = datetime.datetime.strptime("{}-{}".format(year, month_day), '%Y-%m-%d')
        print("\nYear to date {}".format(year))
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
