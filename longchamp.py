# pylint: disable=no-member
from pystrava import Strava
import datetime
import configparser

# Configutation input
config = configparser.RawConfigParser()
config.read('config.properties')
config_dict = dict(config.items('CONFIG'))

if __name__ == "__main__":

    config.read('.credentials.properties')
    cred_dict = dict(config.items('CREDENTIALS'))

    client = Strava(client_id=cred_dict["client_id"],
                    client_secret=cred_dict["client_secret"],
                    callback=cred_dict["callback"],
                    scope="activity:read_all,profile:read_all",
                    email=cred_dict["user"],
                    password=cred_dict["password"])

    segments = [3572501, 17109958]
    # segments = [17109958]
    
    for seg in segments:
        lonlon_day = {}
        record = None
        for year in list(range(int(config_dict["year_start"]), datetime.datetime.now().year + 1)):
            lonlon_efforts = []
            date_ranges = [
                {"start": "01-01", "end": "03-31"},
                {"start": "04-01", "end": "06-30"},
                {"start": "07-01", "end": "09-30"},
                {"start": "10-01", "end": "12-31"}
            ]
            for date_range in date_ranges:
                lonlon_effort = client.get_segment_efforts(seg, start_date_local=f"{year}-{date_range['start']}", end_date_local=f"{year}-{date_range['end']}")
                for l in lonlon_effort:
                    if record == None or l.moving_time < record.moving_time :
                        record = l
                    if not f"{l.start_date}"[:10] in lonlon_day:
                        lonlon_day[f"{l.start_date_local}"[:10]] = {"count": 0, "distance": 0.0, "time": 0}
                    lonlon_day[f"{l.start_date}"[:10]]["count"] += 1
                    lonlon_day[f"{l.start_date}"[:10]]["distance"] += float(l.distance)
                    lonlon_day[f"{l.start_date}"[:10]]["time"] += l.moving_time.total_seconds()

        nb_rides = 0
        lonlon_list = []
        for day in lonlon_day:
            nb_rides += 1
            lonlon_day[day]["average_speed"] =  round((lonlon_day[day]['distance'] / 1000) / (lonlon_day[day]['time'] / 3600),2)
            lonlon_list.append({"day": day, **lonlon_day[day]})

        print(f"\nTotal nombre de sorties à Longchamp: {nb_rides}")

        record_avg = round((float(record.distance) / 1000) / (record.moving_time.total_seconds() / 3600),2)
        print(f"\nRecord: {record.moving_time} ({record_avg} km/h), le {record.start_date_local}")

        lonlon_list_speed = sorted(lonlon_list, key=lambda x: x["average_speed"], reverse=True)
        rank = 0
        for l in lonlon_list_speed:
            rank += 1
            l["rank"] = rank

        print(f"\nTop {config_dict['top']}")
        print("---------------------------------------\n")

        for i, d in enumerate(lonlon_list_speed):
            print(f"{i+1}) {d['day']}: {d['count']} tours | {d['average_speed']} km/h")
            if i >= int(config_dict["top"]) - 1:
                break
        
        print(f"\n{config_dict['top']} Dernières")
        print("----------------------------------------------------------\n")
        lonlon_list_date = sorted(lonlon_list_speed, key=lambda x: x["day"], reverse=True)
        for i, d in enumerate(lonlon_list_date):
            print(f"{i+1}) {d['day']}: {d['count']} tours | {d['average_speed']} km/h | Classement {d['rank']}/{nb_rides}")
            if i >= int(config_dict["top"]) - 1:
                break
