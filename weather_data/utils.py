import datetime
import calendar
import numpy as np
import os

def yearly_pattern(year):
    # Yearly behaviour pattern
    first_day = datetime.date(year, 1, 1).strftime("%A")

    if calendar.isleap(year):
        year_len = 366
    else:
        year_len = 365

    Year_behaviour = np.zeros(year_len)

    dict_year = {'Monday': [5, 6],
                 'Tuesday': [4, 5],
                 'Wednesday': [3, 4],
                 'Thursday': [2, 3],
                 'Friday': [1, 2],
                 'Saturday': [0, 1],
                 'Sunday': [6, 0]}

    for d in dict_year.keys():
        if first_day == d:
            Year_behaviour[dict_year[d][0]:year_len:7] = 2
            Year_behaviour[dict_year[d][1]:year_len:7] = 2

    year_behaviour_hourly = Year_behaviour.repeat(24)
    year_behaviour_hourly[0:6] = 3
    for i in range(8):  # Nachtabsenkung von 22 bis 6 Uhr (8 Stnden)
        year_behaviour_hourly[22:][i:len(year_behaviour_hourly):24] = 3
    return year_behaviour_hourly


def is_float(string):
    """ True if given string is float else False"""
    try:
        return float(string)
    except ValueError:
        return False


def load_files(pfad, separator):
    daten = []
    with open(pfad, 'r') as f:
        d = f.readlines()
        for i in d:
            k = i.rstrip().split(separator)
            daten.append([float(i) if is_float(i) else i for i in k])

    daten = np.array(daten, dtype='float')
    return daten

def weather_data():
    # Datenimport
    my_path = os.path.dirname(os.getcwd())

    pfad1 = os.path.join(my_path, 'weather_data', 'Nordhausen-hour.dat')
    pfad2 = os.path.join(my_path, 'weather_data', 'Nordhausen-Nord-90°-hour.dat')
    pfad3 = os.path.join(my_path, 'weather_data', 'Nordhausen-Ost-90°-hour.dat')
    pfad4 = os.path.join(my_path, 'weather_data', 'Nordhausen-Süd-0°-Horizontal-strahlung-hour.dat')
    pfad5 = os.path.join(my_path, 'weather_data', 'Nordhausen-Süd-90°-hour.dat')
    pfad6 = os.path.join(my_path, 'weather_data', 'Nordhausen-West-90°-hour.dat')

    Ta = load_files(pfad1, separator=",")[:, 4]  # Außentemperatur
    GTN = load_files(pfad2, separator=",")[:, 4] / 1000
    GTO = load_files(pfad3, separator=",")[:, 4] / 1000
    GTH = load_files(pfad4, separator=",")[:, 4] / 1000
    GTS = load_files(pfad5, separator=",")[:, 4] / 1000
    GTW = load_files(pfad6, separator=",")[:, 4] / 1000

    return Ta, GTN, GTO, GTH, GTS, GTW







