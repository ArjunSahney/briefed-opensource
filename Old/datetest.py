import datetime

# curr_date = datetime.now().strftime('%Y-%m-%d')
# print(curr_date)
# Get the current date
today = datetime.date.today()
# Get the day of the week (0 = Monday, 6 = Sunday)
day_of_week = today.weekday()
# List of day names
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# Get the day name
day_name = day_names[day_of_week]
# Get the month and day
month = today.month
day = today.day
year = today.year
curr_date = f"{year}-{month}-{day}"

print(curr_date)