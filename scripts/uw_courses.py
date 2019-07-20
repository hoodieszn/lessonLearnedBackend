
import requests
import json
import csv


api_key = "?key="
subjects_endpoint = "https://api.uwaterloo.ca/v2/codes/subjects.json"
groups_endpoint = "https://api.uwaterloo.ca/v2/codes/groups.json"
courses_endpoint = "https://api.uwaterloo.ca/v2/courses.json"


# Our mapping: Degrees -> Courses
# UW: Group -> Subject -> Courses

# This is "Groups"
degrees = []

ignored_degrees = ['REN', 'STJ', 'THL', 'VPA', 'STP', 'CGC']

def get_all_subjects_for_group(group):
    subjects = []
    r = requests.get(subjects_endpoint+api_key)
    json_data = r.json()

    for subject in json_data['data']:
        sub_group = subject['group']
        if sub_group == group:
            subjects.append(subject['subject'])

    return subjects

def get_all_groups():
    r = requests.get(groups_endpoint+api_key)
    json_data = r.json()

    for group in json_data['data']: 
        group_code = group['group_code']
        group_name = group['group_short_name']

        if group_code not in ignored_degrees:
            # print(group_code, group_name)
            degrees.append((group_code, group_name))

    print(degrees)


def get_all_courses_for_subjects(degree, subjects):
    r = requests.get(courses_endpoint+api_key)
    json_data = r.json()

    courses = []
    for course in json_data['data']: 
        if course['subject'] in subjects:
            courses.append(course['subject'] + " " + course['catalog_number'])
            # print(course['subject'] + " " + course['catalog_number'])

    return courses

def create_csv(degree, rows):
    # 3,SCI 206,2019-07-16 02:51:08.720949+00,3

    with open('courses.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        for row in rows:
            r = [row, '2019-07-16 02:51:08.720949+00', degree]
            writer.writerow(r)


get_all_groups()
subjects = get_all_subjects_for_group(degrees[7][0])
courses = get_all_courses_for_subjects(degrees[7][1], subjects)
create_csv("3", courses)
