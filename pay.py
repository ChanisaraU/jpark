def week(dd):
    switcher = {
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
        "7": "Sunday"
    }
    return switcher.get(dd, "Please type only number (1-7)")


day = input("type num day: ")
day_name = week(day)
print(day_name)