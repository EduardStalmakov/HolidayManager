from datetime import datetime
from datetime import date
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import holidays_loc
from config import parameters
from config import Api_url

#Variable to keep running the main_menu program and see if changes were made
keep_running = True
have_there_been_changes = False



# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dataclass
class Holiday:
    name: str
    date: datetime
      
    def __str__ (self):
        # String output
        # Holiday output when printed.
        return (f'{self.name}  ({self.date})')
          
           
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------

class HolidayList:
    def __init__(self):
       self.innerHolidays = []

    def addHoliday(self,holidayObj):
        # Use innerHolidays.append(holidayObj) to add holiday
        #Check if the holiday is already in the list
        is_holiday_in_list = holidayObj in self.innerHolidays

        #If it is not in the holiday list, add to the holiday list
        if is_holiday_in_list == False:
            self.innerHolidays.append(holidayObj)
        # print to the user that you added a holiday
            print(f"Sucess: \n {holidayObj} has been added to the holiday list." )
            global have_there_been_changes
            have_there_been_changes = True
        else:
            print("This holiday is already in the list")

    def findHoliday(self,HolidayName, Date):
        # Find Holiday in innerHolidays
        for i in range(len(self.innerHolidays)):
            inner_holidays_dict = self.innerHolidays[i].__dict__
            if HolidayName == inner_holidays_dict['name'] and Date == inner_holidays_dict['date']:
                return (f"{inner_holidays_dict['name']} ({inner_holidays_dict['date']})")
                
        # Return Holiday
       
    def removeHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays by searching the name and date combination.
        holiday_successfuly_removed = False

        
        for p in self.innerHolidays:
            if p.name == HolidayName and p.date == Date:
                self.innerHolidays.remove(p)
                print(f"Success: \n {p} has been removed from the holiday list")
                global have_there_been_changes
                have_there_been_changes = True
                holiday_successfuly_removed = True
                break
        
        if holiday_successfuly_removed == False:
            print(f"Error: \n {HolidayName} not found")

            

    def read_json(self,filelocation):
        # Read in things from json file location
        holidays_file = open(filelocation).read()
        holidays_file_json = json.loads(holidays_file)
        #Create Holiday Object
        for i in holidays_file_json['holidays']:
        # add holidays to inner list.
            holiday_object = Holiday(i['name'],i['date'])
            self.innerHolidays.append(holiday_object)
            
            
    def save_to_json(self,filelocation):
        # Write out json file to selected file.
        json__holiday_list = [h.__dict__ for h in self.innerHolidays]
        json_holiday_dict = {
            'holidays': json__holiday_list
        }
        with open(filelocation,'w') as holidayfile:
            json.dump(json_holiday_dict, holidayfile)



        
    def scrapeHolidays(self):
       # Scrape Holidays from https://www.timeanddate.com/holidays/us 
        parameters = ['2020', '2021', '2022', '2023', '2024']
        
        #For each year year in the parameters list, use a get request
        for i in parameters:
            response = requests.get(f"{holidays_loc}/{i}").text
            soup = BeautifulSoup(response, 'html.parser')
            tbody = soup.find('tbody')

            dates = tbody.find_all('th')
            titles = tbody.find_all('a')

            #for every title, find the name and the date
            for j in range(len(titles)):
                date_in_month_day = dates[j].string
                date_in_month_day_year = date_in_month_day +', '+(i)
                correctly_formatted_date = datetime.strptime(date_in_month_day_year,'%b %d, %Y').strftime('%Y-%m-%d')
                holiday_name = titles[j].string

                #store as a holiday object
                Holiday_object1 = Holiday(holiday_name,correctly_formatted_date)
               
                #Check if the holiday is already in the list
                is_holiday_in_list = (Holiday(holiday_name, correctly_formatted_date)) in self.innerHolidays

                #If it is not in the holiday list, add to the holiday list
                if is_holiday_in_list == False:
                    self.innerHolidays.append(Holiday_object1)

        # Handle any exceptions.    
           

    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)
    

    def filter_holidays_by_week(self, year, week_number):
        
        #create list to hold holiday objects as a list of dictionaries
        holidays_list_by_filter_dict = [h.__dict__ for h in self.innerHolidays]
    
        #Use lambda to filter of week number and year
        #return filtered results as  holiday list
        holiday = filter(lambda p: str(date.fromisoformat(p['date']).isocalendar().week) == str(week_number) 
                            and str(date.fromisoformat(p['date']).isocalendar().year) == str(year), 
                            holidays_list_by_filter_dict)
        holiday_list = list(holiday)
        return (holiday_list)


    def displayHolidaysInWeek(self,holidayList):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        
        # Create Holiday objects and store in list
        list_of_holiday_objects_within_filter = []
        for i in range(len(holidayList)):
            list_of_holiday_objects_within_filter.append(Holiday(holidayList[i]['name'],holidayList[i]['date']))

        #Print each object
        #Printing objects using the holiday__str__method
        for p in list_of_holiday_objects_within_filter:
            print(p)
        
        

    def getWeather(self,weekNum, year):
        # Convert weekNum to range between two days
        starting_week_day = date.fromisocalendar(year,weekNum,1)
        ending_week_day = date.fromisocalendar(year,weekNum,7)
        # Use Try / Except to catch problems

        # Query API for weather in that week range
        
        # Format weather information and return weather string.
        weather_response = requests.get(f'{Api_url}/{starting_week_day}/{ending_week_day}', params=parameters).text
        weather_response_json = json.loads(weather_response)
        weather_day_list_of_dict = []

        for i in range(len(weather_response_json['days'])):
            weather_day_dict = {}
            weather = weather_response_json['days'][i]['icon']
            weather_day = weather_response_json['days'][i]['datetime']
            weather_day_dict['day'] = weather_day
            weather_day_dict['weather'] = weather
            weather_day_list_of_dict.append(weather_day_dict)
        return weather_day_list_of_dict

    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        current_week = datetime.now().date().isocalendar().week
        current_year = datetime.now().date().isocalendar().year
        # Use your filter_holidays_by_week function to get the list of holidays 
        # for the current week/year
        list_of_current_holidays = self.filter_holidays_by_week(current_year,current_week)
        # Use your displayHolidaysInWeek function to display the holidays in the week
        display_weather = str(input("Would you like to see this week's weather? [y/n]"))
        if display_weather == 'y':
            dict_of_weather = self.getWeather(current_week,current_year)

            #Check to see if holiday date is the same as weather date, print holiday and weather
            print(f"\n These are the holidays for this week: \n ======================================")
            for p in list_of_current_holidays:
                for i in range(len(dict_of_weather)):
                    if p['date'] == dict_of_weather[i]['day']:
                        print(f"{p['name']} ({p['date']}) - {dict_of_weather[i]['weather']}")


           # If user doesn't want to see the weather, print only the holidays 
        else:
            self.displayHolidaysInWeek(list_of_current_holidays)


    def start_up(self):
        print('Holiday Management \n ==================') 
        print(f'There are {self.numHolidays()} holidays stored in the system')
    
    def main_menu(self):
        main_menu_options = {
            1: 'Add a Holiday',
            2: 'Remove a Holiday',
            3: 'Save Holiday List',
            4: 'View Holidays',
            5: 'Exit'
        }

        for i in main_menu_options:
            print(f'{i}. {main_menu_options[i]}')

        #Exception handling to ensure an int is typed between 1-5    
        is_user_input_an_int = False
        while is_user_input_an_int == False:

            try:
                user_input = int(input('Select menu option [1-5]:'))
                int(user_input)
                if user_input >= 1 and user_input <6:
                    is_user_input_an_int = True
                else:
                    print("Please type a number between 1-5")
            except ValueError:
                print("This is not a number, try again")


        return user_input

    def run_main_menu_selection(self, user_input):
        # Add a holiday
        if user_input == 1:
            keep_selection_running = True
            while keep_selection_running == True:
                print("Add a Holiday \n =============")
                holiday_name = str(input("Holiday: "))

                #Ensure an invalid date is entered, if not reprompt
                invalid_date = True
                while invalid_date == True:
                    holiday_date = str(input("Date (YYYY-MM-DD): "))
                    try:
                        date.fromisoformat(holiday_date)
                        holiday_object = Holiday(holiday_name,holiday_date)
                        self.addHoliday(holiday_object)
                        invalid_date = False
                    except:
                        print("Invalid date. Please try again")
                        invalid_date = True
                #Ask if the user wants to continue adding a holiday
                want_to_keep_running = str(input("\nWant to continue adding holiday [y/n]: "))
                if want_to_keep_running == 'n':
                    keep_selection_running = False

        # Remove a holiday
        elif user_input ==2:
            keep_selection_running = True
            while keep_selection_running == True:
                print("Remove a Holiday \n =============")
                holiday_name = str(input("Holiday: "))
                holiday_date = str(input("Date (YYYY-MM-DD): "))
                self.removeHoliday(holiday_name,holiday_date)
                
                want_to_keep_running = str(input("\nWant to continue removing a holiday [y/n]: "))
                if want_to_keep_running == 'n':
                    keep_selection_running = False
               
        #Save holiday list
        elif user_input ==3:
            keep_selection_running = True
            while keep_selection_running == True:
                print("Save Holiday List \n =============")
                save_changes  = str(input("Are you sure you want to save your changes? [y/n]: "))
                if save_changes == 'y':
                    self.save_to_json('holidays.json')
                    print("Success: \n Your changes have been saved")
                    keep_selection_running = False
                else:
                    print("Canceled: \n Holiday list file save canceled")
                    want_to_keep_running = str(input("\nWant to continue to save changes? [y/n]: "))
                    if want_to_keep_running == 'n':
                        keep_selection_running = False
        # View holidays
        elif user_input ==4:
            keep_selection_running = True
            while keep_selection_running == True:
                print("View Holidays \n =============")
                # Get input for holiday year and week number
                holiday_year = str(input("Which Year?: "))
                holiday_week = str(input("Which Week? #[1-52, Leave blank for the current week]: "))

                #If holiday week is blank, view current week
                if holiday_week == "":
                    self.viewCurrentWeek()
                    want_to_keep_running = str(input("\nWant to continue viewing holidays [y/n]: "))
                    if want_to_keep_running == 'n':
                        keep_selection_running = False
                # If holiday week is not blank, view the desired selection
                else:
                    holidays = self.filter_holidays_by_week(holiday_year,holiday_week)
                    print(f"\n These are the holidays for {holiday_year} week #{holiday_week} \n ======================================")
                    self.displayHolidaysInWeek(holidays)
                    want_to_keep_running = str(input("\nWant to continue viewing holidays [y/n]: "))
                    if want_to_keep_running == 'n':
                        keep_selection_running = False
        # exit the program, 
        elif user_input ==5:
            print("Exit \n =============")
            global have_there_been_changes

            # if changes were not made, run this prompt
            if have_there_been_changes == False:
                exit = str(input("Are you sure you want to exit? [y/n]: "))
                if exit == 'y':
                    global keep_running 
                    keep_running = False
                    print('Goodbye!')

            # If changes were made, run this prompt
            else:
                print("Are you sure you want to exit? \n Your changes will be lost.")
                exit = str(input("[y/n]: "))
                if exit == 'y':
                    keep_running = False
                    print('Goodbye!')

        # If an invalid input is typed, try again (backup data validation in case the first fails)
        else:
            print("Invalid input, please try again")
        
        

        


     
            
            
            




def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    initialize_holiday_list = HolidayList()
    # 2. Load JSON file via HolidayList read_json function
    initialize_holiday_list.read_json('holidays.json')
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    initialize_holiday_list.scrapeHolidays()
    # 3. Create while loop for user to keep adding or working with the Calender
    initialize_holiday_list.start_up()
    while keep_running == True:
    # 4. Display User Menu (Print the menu)
    # 5. Take user input for their action based on Menu and check the user input for errors
        user_input = initialize_holiday_list.main_menu()
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
        initialize_holiday_list.run_main_menu_selection(user_input)
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 


if __name__ == "__main__":
    main();


# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.





