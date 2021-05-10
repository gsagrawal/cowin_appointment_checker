# cowin_appointment_checker
To get real time notification notified whenever there is a 18+ vaccination slots open in gurgaon 


to change the location : change the district code from param (get the district code by checking network calls on cowin app) 



Setup 

1. Install python dependencies
 
 _pip3 install requests schedule_
 
 For telegram setup install following dependencies 
 
_pip3 install telebot telethon_
 
2. Setup telegram bot and api 

#TODO: add steps to generate telegram api/hash/auth_token/channel_name (or receiver id for telegram) 

#refer to https://www.geeksforgeeks.org/send-message-to-telegram-user-using-python/ for now 

3. Create one public channel in telegram, use the public share link name (and update it in the code) (except t.me, only the name)
4. Run the app using  _python3 appointment_checker.py '<api_id>' '<api_hash>' <send_telgram_notification>"_



Drop me a mail at gsagrawal@gmail.com for any questions/concerns 

