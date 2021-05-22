# cowin_appointment_checker

There are two scripts

1 : appointment_checker.py : This is to check appointment and notify the user.

2: slot_booking_bot.py : This check and book the appointment. It needed input like phone number/ otp and captcha which are valid for 15 mintues i.e you have to run it again after each 15 minutes


**Readme for appointment_checker.py **


 To get real time notification notified whenever there is a 18+ vaccination slots open in gurgaon


 to change the location : change the district code from param (get the district code by checking network calls on cowin app)



 Setup

 1. Install python dependencies

  _pip3 install requests schedule_

  For telegram setup install following dependencies

 _pip3 install telebot telethon_

 2. If you dont need notifications then run the code using 'python3 appointment_checker.py False'

 3. Setup telegram bot and api

 #TODO: add steps to generate telegram api/hash/auth_token/channel_name (or receiver id for telegram)

 #refer to https://www.geeksforgeeks.org/send-message-to-telegram-user-using-python/ for now

 4. Create one public channel in telegram, use the public share link name  (except t.me, only the name)

 5. Run the app using  _python3 appointment_checker.py True '<api_id>' '<api_hash>' '<bot_token>' '<channel_id>' "_


**Readme for slot_booking_bot.py  : **

Why this script : Right now due to heavy load by simple notification you cant book the appointment

Issue with this script : It needs a token and captcha which is valid for 15 minutes only. So After each 15 mnutes you have to run the script again. (or better after 12 minutes run the script in another terminal and close the old one later)

How to run the script :
1. Basic setup, install python libs
 _pip3 install requests schedule pyjwt_
 _brew install libffi cairo_
 _pip3 install cairosvg_
2. Better to hard code your phone number, district id, preffered center id and preffered vaccine. In case if you dont provide preffere center and vaccine, it will try to book the first availble one.
3. Programm will ask you to enter OTP and then captcha.
4. Check the captcha from captcha.png file or copy the svg tag and view it in this editor : https://www.w3schools.com/html/tryit.asp?filename=tryhtml_svg_circle
5. Enter the correct captcha
6. Now it will check for avaialble appointment and as soon as it finds one , it will book it.

*This code is a very basic version of code (with less comments and prints).For now it works, i have personally used it to book appointments for my relatives

**Feel free to contribute in this code.
***Next step is to build a telegram bot which takes care of this OTP input and captcha input.


Drop me a mail at gsagrawal@gmail.com for any questions/concerns

