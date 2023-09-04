# pylint: disable=no-member
import datetime
import configparser
import requests
from auth import refresh_token

def longchamp():
    # Configutation input
    config = configparser.RawConfigParser()
    config.read('config.properties')
    config_dict = dict(config.items('CONFIG'))

    access_token = refresh_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    segments = [3572501, 17109958]
    # segments = [17109958]
    for seg in segments:
        lonlon_day = {}
        record = {}
        for year in list(range(int(config_dict["year_start"]), datetime.datetime.now().year + 1)):
            date_ranges = [
                {"start": "01-01", "end": "03-31"},
                {"start": "04-01", "end": "06-30"},
                {"start": "07-01", "end": "09-30"},
                {"start": "10-01", "end": "12-31"}
            ]
            for date_range in date_ranges:
                parameters = {
                     "segment_id": seg,
                     "start_date_local": f"{year}-{date_range['start']}",
                      "end_date_local": f"{year}-{date_range['end']}",
                      "per_page": 200
                }
                resp = requests.get("https://www.strava.com/api/v3/segment_efforts",
                                    params=parameters, headers=headers, timeout=300)
                lonlon_efforts = resp.json()
                if len(lonlon_efforts) == 200:
                    print("Warning missing efforts")
                for effort in lonlon_efforts:
                    if not record or effort["moving_time"] < record["moving_time"] :
                        record = effort
                    if not f"{effort['start_date']}"[:10] in lonlon_day:
                        lonlon_day[f"{effort['start_date_local']}"[:10]] = {"count": 0,
                                                                            "distance": 0.0, 
                                                                            "time": 0
                                                                            }
                    lonlon_day[f"{effort['start_date']}"[:10]]["count"] += 1
                    lonlon_day[f"{effort['start_date']}"[:10]]["distance"] += float(effort['distance'])
                    lonlon_day[f"{effort['start_date']}"[:10]]["time"] += effort['moving_time']

        nb_rides = 0
        lonlon_list = []
        for day, metrics in lonlon_day.items():
            nb_rides += 1
            metrics["average_speed"] =  round((metrics['distance'] / 1000)
                                        / (metrics['time'] / 3600),2)
            lonlon_list.append({"day": day, **metrics})

        print(f"\nTotal nombre de sorties à Longchamp: {nb_rides}")

        record_avg = round((float(record['distance']) / 1000) / (record['moving_time'] / 3600),2)
        print(f"\nRecord: {str(datetime.timedelta(seconds=record['moving_time']))} ({record_avg} km/h), le {record['start_date_local']}")

        lonlon_list_speed = sorted(lonlon_list, key=lambda x: x["average_speed"], reverse=True)
        rank = 0
        for lonlon_day in lonlon_list_speed:
            rank = rank + 1
            lonlon_day["rank"] = rank

        print(f"\nTop {config_dict['top']}")
        print("---------------------------------------\n")

        for i, day in enumerate(lonlon_list_speed):
            print(f"{i+1}) {day['day']}: {day['count']} tours | {day['average_speed']} km/h")
            if i >= int(config_dict["top"]) - 1:
                break

        print(f"\n{config_dict['top']} Dernières")
        print("----------------------------------------------------------\n")
        lonlon_list_date = sorted(lonlon_list_speed, key=lambda x: x["day"], reverse=True)
        for i, day in enumerate(lonlon_list_date):
            print(f"{i+1}) {day['day']}: {day['count']} tours | {day['average_speed']} km/h | Classement {day['rank']}/{nb_rides}")
            if i >= int(config_dict["top"]) - 1:
                break

if __name__ == "__main__":
    longchamp()