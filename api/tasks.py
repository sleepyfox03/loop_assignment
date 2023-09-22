from datetime import datetime,timedelta
from pytz import timezone
from .models import Reports,MenuHours,BqResults,StoreStatus
# UTC timestamp
#timestamp_utc = '2023-09-18 14:30:00:53500'
 
 

 
# current timestamp to be the max timestamp among all the observations in the first CSV
current_time = "2023-01-25 18:13:22.47922 UTC"
def get_weekday(datetime_str):
    '''Function to get the weekday of the given datetime'''
    dt = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S.%f %Z")
    day = dt.weekday()
    return day
def getLastDate(current_time):
    '''Function to get the last date'''
    x = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f %Z').replace(second=0,microsecond=0)
    x = x  - timedelta(days=1)  
    return x

def convert_to_local(timestamp_utc,target_timezone):
    '''Function to convert the utc time to local time'''
    utc_time = datetime.strptime(timestamp_utc, '%Y-%m-%d %H:%M:%S.%f %Z').replace(second=0,microsecond=0)
    local_time = utc_time.replace(tzinfo=timezone('UTC')).astimezone(timezone(target_timezone))
    return local_time
    
 
        
def calculate_minute_difference(time1,time2):
    '''Function to calcuate minute difference between two timestamps'''
    time1_seconds = time1.hour * 3600 + time1.minute * 60 + time1.second
    time2_seconds = time2.hour * 3600 + time2.minute * 60 + time2.second

 
    time_difference_seconds = time1_seconds - time2_seconds
    return time_difference_seconds / 6
  

def getTodayDate(datetime_str):  
    '''Function to get the date of given datetime string'''              
    x = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f %Z').replace(second=0,microsecond=0)
    return x



 
def generate_report(report_id):
        # Retrieve data for stores from BqResults
        stores = BqResults.objects.all().filter()
        count = 0
        
        
        with open("./static/"+report_id+".csv", 'w') as report_file:
            report_file.write("store_id,uptime_last_hour(in minutes), uptime_last_day_report(in hours), update_report_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)\n")
            count = 0

            for i in stores:
                count += 1
                #For screen recording purpose of the assignment
                #  we are just printing csv data for 15 stores
                #and we have created a reports table which will store status of our csv file 
                if count == 15:
                    break
                #Calculate uptime and downtime for various time periods
                last_hour_report = calculate_uptime_downtime_lasthour(i.store_id,i.timezone_str)
                last_day_report = calculate_uptime_downtime_lastday(i.store_id,i.timezone_str) 
                last_weekday_report = calculate_uptime_downtime_weekday(i.store_id,i.timezone_str) 
                # Write the store data to the CSV file
                report_file.write(f"{i.store_id},{last_hour_report[0]},{last_day_report[0]},{last_weekday_report[0]} ,{last_hour_report[1]},{last_day_report[1]},{last_weekday_report[1]}\n")

    
def calculate_uptime_downtime_lasthour(store_id,timezone_str):
    '''calculate uptime and downtime for lasthour for a given store'''

    #Getting the day for current time
    day = get_weekday(current_time)

    # Calculate the timestamp for the last hour
    last_hour_timestamp = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S.%f %Z") - timedelta(hours=2)
    
    # Retrieve business hours for the specific store and day of the week
    menuHours = MenuHours.objects.filter(store_id=store_id,day = day) 

    if not timezone_str :
        timezone_str = "America/Chicago"

    # Retrieve store status data for the past hour, ordered by timestamp
    storeData = StoreStatus.objects.filter(store_id = store_id,timestamp_utc__gte=last_hour_timestamp).order_by("-timestamp_utc")   # if no business hours for this day , then we will skip calculating the uptime and downtime

    # if no business hours for this day , then we will skip calculating the uptime and downtime
    if not MenuHours:
        return 0 ,0
    
    # Initialize variables for tracking uptime and downtime
    ct = convert_to_local(current_time,timezone_str) 
    temp = convert_to_local(current_time,timezone_str)
    last_hour = temp - timedelta(hours=1)
    uptime,downtime  = 0,0


    flag = 1
    #This loop will iterate records of store data variable
    for i in storeData:
        
        obs_time = convert_to_local(i.timestamp_utc,timezone_str)
        #For each and every store data it will iterate records of menu hours 
        for j in menuHours:
            
            start_time_local = datetime.strptime(j.start_time_local,"%H:%M:%f") 
            end_time_local = datetime.strptime(j.end_time_local,"%H:%M:%f") 

            # Check if the observation time falls within business hours
            if obs_time.time() >= start_time_local.time() and obs_time.time() <= end_time_local.time():
                # check if end_time_local  is less than current time then we will calculate uptime or downtime by subtracting from end_time_local
                # and not from current time.Flag makes sure that this if block  will runs only once
                if end_time_local.time() < convert_to_local(current_time,timezone_str).time() and flag ==1:
                    x = calculate_minute_difference(convert_to_local(current_time,timezone_str).time(),end_time_local.time())
                    flag = 0
                    #if status is active then it will add to uptime else downtime for specific condition
                    if i.status == "active":
                      uptime -= (x )
                    else:
                      downtime -= (x )        
                #this if block is calculating uptime and downtime in minutes for all the condintions
                if i.status == "active":
                    uptime += (temp - obs_time ).seconds / 60
                else:
                    downtime += (temp - obs_time ).seconds / 60
               
                temp = obs_time
               #this if block is checking if observed time is less than last hour
                if obs_time.time() < last_hour.time():
                    
                    if i.status == "active":
                        
                        uptime -= (last_hour - obs_time).seconds / 60
                    else:
                        downtime -= (last_hour - obs_time).seconds / 60     
                    return uptime,downtime
                
            # Handling corner case if observation time falls behind the start time , then it will calculate the
            # remaining time of the observation which falls under the start time and will calculate either it's uptime or downtime.
            elif obs_time.time() < start_time_local.time() and ct.time() >= start_time_local.time() and ct.time() <= end_time_local.time():
                
                if i.status == "active":    
                    uptime += calculate_minute_difference(temp.time(),start_time_local.time())
                else:
                    downtime += calculate_minute_difference(temp.time(),start_time_local.time())
           
                return uptime,downtime
               
           

    if uptime < 0 or downtime < 0:
        uptime,downtime = 0,0
    return uptime,downtime
    

def calculate_uptime_downtime_lastday(store_id,timezone_str):
    ''''''     # Calculate uptime and downtime for the last day '''
    day = get_weekday(current_time) -1 
  
    last_date = getLastDate(current_time)
    day  = last_date.weekday()

    # Retrieve business hours for the specific store and day of the week
    menuHours = MenuHours.objects.filter(store_id=store_id,day = day) 

    # Retrieve store status data for the current day
    storeData = StoreStatus.objects.filter(store_id = store_id,timestamp_utc__contains=last_date.date()).order_by("-timestamp_utc")
    
    if not timezone_str :
        timezone_str = "America/Chicago"


    # if no business hours for this day , then we will skip calculating the uptime and downtime
    if not MenuHours:
        return 0 ,0
 
    uptime_weekday,downtime_weekday  = 0,0
    for i in storeData:
        obs_time = convert_to_local(i.timestamp_utc,timezone_str)
        
        for j in menuHours:
            
            start_time_local = datetime.strptime(j.start_time_local,"%H:%M:%f") 
            end_time_local = datetime.strptime(j.end_time_local,"%H:%M:%f") 
            # Check if the observation time falls within business hours
            if obs_time.time() >= start_time_local.time() and obs_time.time() <= end_time_local.time():
                
                if i.status == "active":
                    uptime_weekday += 1
                else:
                    downtime_weekday += 1
            
    return uptime_weekday,downtime_weekday
    



 
   
    

     

def calculate_uptime_downtime_weekday(store_id,timezone_str):
    ''' Calculate uptime and downtime for the past 7 days (weekdays) '''

    current_date  =  getTodayDate(current_time)  - timedelta(days=1)  
    uptime_weekday,downtime_weekday  = 0,0
    # Loop through the past 7 days
    for k in range(7):
        
         
        last_date = getLastDate(current_time)
        day  = last_date.weekday()


        # Retrieve business hours for the specific store and day of the week
        menuHours = MenuHours.objects.filter(store_id=store_id,day=day) 
        # Retrieve store status data for the current day
        storeData = StoreStatus.objects.filter(store_id = store_id,timestamp_utc__contains=current_date.date()).order_by("-timestamp_utc")
        

        if not timezone_str :
            timezone_str = "America/Chicago"
       
        # if no business hours for this day , then we will skip calculating the uptime and downtime
        if not MenuHours:
            continue
    
        # Iterate through store status data and business hours
        for i in storeData:
            obs_time = convert_to_local(i.timestamp_utc,timezone_str)
            
            for j in menuHours:
                
                start_time_local = datetime.strptime(j.start_time_local,"%H:%M:%f") 
                end_time_local = datetime.strptime(j.end_time_local,"%H:%M:%f") 

                # Check if the observation time falls within business hours # Check if the observation time falls within business hours
                if obs_time.time() >= start_time_local.time() and obs_time.time() <= end_time_local.time():
                    if i.status == "active":
                        uptime_weekday += 1
                    else:
                        downtime_weekday += 1
                
        # Move to the previous day for the next iteration
        current_date = current_date - timedelta(days=1)    
      
    return uptime_weekday,downtime_weekday    

