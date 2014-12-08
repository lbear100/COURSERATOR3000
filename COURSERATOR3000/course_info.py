#!/usr/bin/env python3

import re
from datetime import datetime, timedelta

try:
    from . import uwapi # relative import
except SystemError: # not being used as a module
    import uwapi # normal import

def parse_date(value, default_date):
    components = list(map(int, re.findall("\d+", value)))
    assert 2 <= len(components) <= 3
    if len(components) == 2: # month and day specified
        return datetime(default_date.year, components[0], components[1])
    return datetime(components[0], components[1], components[2]) # year, month, and day specified

def get_class_times(description, default_start_date, default_end_date):
    #wip: do something with "is_closed" and "enrollment_capacity" and "enrollment_total", like an option to use even closed classes
    if description["start_time"] is None or description["end_time"] is None: # no specified time
        return []
    
    # parse daily times into offsets from the beginning of its day
    hours, minutes = map(int, description["start_time"].split(":"))
    daily_start = timedelta(minutes=minutes, hours=hours)
    hours, minutes = map(int, description["end_time"].split(":"))
    daily_end = timedelta(minutes=minutes, hours=hours)
    
    # parse weekdays into a list of 2-tuples containing the offset of the course from the beginning of its week and its duration
    weekdays = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4, "S": 5, "Su": 6}
    weekly_classes = []
    for day in re.findall(r"Th|Su|M|T|W|F|S", description["weekdays"]):
        current_day = timedelta(days=weekdays[day])
        weekly_classes.append((current_day + daily_start, current_day + daily_end))
    
    # parse start/end dates
    start = parse_date(description["start_date"], default_start_date) if description["start_date"] is not None else default_start_date
    end = parse_date(description["end_date"], default_end_date) if description["end_date"] is not None else default_end_date
    end = end + timedelta(days=1) # add one day to compare against the end of the day
    
    # generate class list
    result = []
    current_date = start - timedelta(days=start.weekday()) # beginning of the week containing the start date
    while current_date < end:
        for class_start_offset, class_end_offset in weekly_classes:
            class_start, class_end = current_date + class_start_offset, current_date + class_end_offset
            if class_start >= start and class_end < end:
                result.append((class_start, class_end))
        current_date = current_date + timedelta(weeks=1)
    return result

def get_courses_data(term, course_list):
    assert isinstance(term, int)
    result = {}
    for course in course_list:
        assert isinstance(course, str)
        subject, catalog_number = re.match("^\s*([a-zA-Z]+)\s*(\d\w*)\s*$", course).groups()
        assert subject and catalog_number
        result[course] = uwapi.uwapi("terms/{0}/{1}/{2}/schedule".format(term, subject, catalog_number))
    return result

def get_courses_sections(courses_data, default_start_date, default_end_date):
    result = {}
    for course_name, course_data in courses_data.items():
        for section in course_data:
            times = []
            for classes in section["classes"]:
                times += get_class_times(classes["date"], default_start_date, default_end_date)
            result[(course_name, section["section"])] = sorted(times, key=lambda x: x[0])
    return result

def get_section_entries(courses_data, section_list):
    result = {}
    for course_name, section_name in section_list:
        for section in courses_data[course_name]:
            if section["section"] == section_name:
                result[(course_name, section_name)] = section
    return result

if __name__ == "__main__":
    courses_data = get_courses_data(1151, ["CS240"])
    print(get_courses_sections(courses_data, datetime(2015, 1, 5), datetime(2015, 5, 1)))