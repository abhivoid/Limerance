import csv
import argparse
from datetime import datetime, timedelta
from pytz import timezone


def read_schedule(file_name):
    """
    Read the weekly schedule from a CSV file and return a list of tuples.
    Each tuple contains the start and end time of a scheduled event in minutes since midnight.
    """
    schedule = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            start_time = datetime.strptime(row[0], '%m/%d/%Y %I:%M %p')
            end_time = datetime.strptime(row[1], '%m/%d/%Y %I:%M %p')
            start_minutes = start_time.time().hour * 60 + start_time.time().minute
            end_minutes = end_time.time().hour * 60 + end_time.time().minute
            schedule.append((start_minutes, end_minutes))
    return schedule


def compare_schedules(schedule1, schedule2, time_zone1, time_zone2, max_time_diff):
    """
    Compare two weekly schedules and return a list of tuples representing the free time slots.
    """
    tz1 = timezone(time_zone1)
    tz2 = timezone(time_zone2)
    free_slots = []
    for i in range(len(schedule1) - 1):
        end_time1 = tz1.localize(datetime.now().replace(hour=schedule1[i][1]//60, minute=schedule1[i][1]%60, second=0, microsecond=0))
        start_time1 = tz1.localize(datetime.now().replace(hour=schedule1[i+1][0]//60, minute=schedule1[i+1][0]%60, second=0, microsecond=0))
        duration1 = (start_time1 - end_time1).total_seconds() // 60

        for j in range(len(schedule2) - 1):
            end_time2 = tz2.localize(datetime.now().replace(hour=schedule2[j][1]//60, minute=schedule2[j][1]%60, second=0, microsecond=0))
            start_time2 = tz2.localize(datetime.now().replace(hour=schedule2[j+1][0]//60, minute=schedule2[j+1][0]%60, second=0, microsecond=0))
            duration2 = (start_time2 - end_time2).total_seconds() // 60

            time_diff = abs((start_time1 - start_time2).total_seconds()) // 60
            if time_diff <= max_time_diff and start_time1 <= end_time2 and start_time2 <= end_time1:
                break
        else:
            if duration1 > 0:
                free_slots.append((end_time1.strftime('%m/%d/%Y %I:%M %p'), start_time1.strftime('%m/%d/%Y %I:%M %p'), duration1))
    return free_slots




def main():
    parser = argparse.ArgumentParser(description='Compare a person\'s weekly schedule to a relative\'s weekly schedule')
    parser.add_argument('schedule_file', type=str, help='file name of the person\'s weekly schedule in CSV format')
    parser.add_argument('relative_schedule_file', type=str, help='file name of the relative\'s weekly schedule in CSV format')
    parser.add_argument('time_zone', type=str, help='time zone of the person\'s weekly schedule (e.g. US/Eastern)')
    parser.add_argument('relative_time_zone', type=str, help='time zone of the relative\'s weekly schedule (e.g. US/Pacific)')
    parser.add_argument('max_time_diff', type=int, help='maximum time difference in minutes between events in the schedules')
    args = parser.parse_args()

    schedule1 = read_schedule(args.schedule_file)
    schedule2 = read_schedule(args.relative_schedule_file)
    free_slots = compare_schedules(schedule1, schedule2, args.time_zone, args.relative_time_zone, args.max_time_diff)
    
    if free_slots:
        print("You have free time slots:")
        for slot in free_slots:
            if slot[2]>0:
             print(f"{slot[0]} - {slot[1]} ({slot[2]} minutes)")
    else:
        print("You and your relative do not have any free")

if __name__ == '__main__':
    main()
