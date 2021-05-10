import requests
import json
import sys
from datetime import datetime
import schedule
import time
import random
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events


#TODO: add readme on how to get api_id and api_hash
api_id='<telegram_app>'
api_hash='<telegram_app_hash>'
phone='<add your phone number>' #this is needed when connection with bot is not authenticated
bot_token='<bot-toekn>'
#TODO: add readme on how to get chat_id/channel name
channel_id = '<channel_id>'  #to which channel you want to send the message (this is my channel)


already_notified={}
send_telegram_notification = False

def sendNotification(message):

  if not send_telegram_notification :
    print ("sending message to console :",message,str(datetime.now()),send_telegram_notification)
    return
    pass

  client = TelegramClient('bot-session', api_id, api_hash).start(bot_token=bot_token)
  client.connect()
  if not client.is_user_authorized():
      client.send_code_request(phone)
      # signing in the client
      client.sign_in(phone, input('Enter the code: '))

  try:
      # sending message to a channel using telegram client.
      print ("sending message to telegram :",message,str(datetime.now()),send_telegram_notification)
      entity=client.get_entity(channel_id)
      client.send_message(entity=entity, message=message)
      pass
  except Exception as e:
      # there may be many error coming in while like peer
      # error, wwrong access_hash, flood_error, etc
      print("error",e)

  # disconnecting the telegram session
  client.disconnect()


def schedule_check_appointments():
  #scheduling at random frequency between 1 to 5 seconds.
  time_span = random.randint(1, 2)
  schedule.clear()
  #print(f'Scheduled in {time_span} seconds',str(datetime.now()))
  schedule.every(time_span+0.2).seconds.do(check_appointments)
  pass

def check_appointments():
  response = requests.get(url=url,params=params,headers=headers)

  if response.status_code != 200:
    print("error in fetching data.",response.status_code, response.content)

  else:
    contents = json.loads(response.content)
    centers=contents["centers"]
    #print("total centers are:",str(len(centers)))
    notifications={}
    for c in centers:
      #there are multiple sessions i.e days for which appoints could be available. TODO: to send different notification message for each date.
      for session in c["sessions"]:
        if (session["min_age_limit"] == 18 and session["available_capacity"] > 1 ):  # no point of sending notification with 1 slot as it will get filled
          center_name=c["name"]
          try:
            #ignore already notified centers to avoid flood of notifications
            data=already_notified[center_name]
          except KeyError:
            notifications[center_name]=(c,session["available_capacity"])
            already_notified[center_name]=True
          break
      pass
    pass

    if len(notifications)>0:
      #print("Available schedules :",notifications)
      mesasge =  build_notification(notifications)
      sendNotification(mesasge)
      pass

  #print("done")
  print(".",end =" ",flush=True)
  schedule_check_appointments()
  return schedule.CancelJob

def build_notification(tele_notifications):
  message=""
  for name,value in tele_notifications.items():
    center=value[0]
    message = message + "Avalaiblity at : "+name+", pin code: "+str(center["pincode"])+", Slots: "+str(value[1])+", Address: " + center["address"]+"\n"
  return message

# district_id 118 is for gurgaon
# change the date to today's date
today_date = datetime.today().strftime("%d-%m-%Y")
params= {"district_id":188,"date":datetime.today().strftime(today_date)}

print("checking for appointment")

url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict"

print(url,params)

headers ={
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9,de-AT;q=0.8,de;q=0.7',
  'cache-control': 'max-age=0',
  'if-none-match': 'W/"70af-IG18Mu2z2MCbpqHXH1z9GP3y+WU"',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
  'sec-ch-ua-mobile': '?0',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

def run():
    schedule_check_appointments()
    #sendNotification("test message. Please ignore")
    while True:
        schedule.run_pending()
        time.sleep(1)
    pass
pass


if __name__ == "__main__":
  args = sys.argv
  if len(args) > 1 :
      send_telegram_notification = eval(args[1])
      if send_telegram_notification and len(args) == 6 :
          api_id = args[2]
          api_hash = args[3]
          bot_token = args[4]
          channel_id = args[5]
          print("api id: {}, api_hash: {}, bot_token:{}, channel_id: {} ".format(api_id,api_hash,bot_token,channel_id))
          run()
      elif not send_telegram_notification:
          run()
      pass
  pass
  print("run with python3 appointment_checker.py True '<api_id>' '<api_hash>' <bot_token> <channel_id>")
  print("or python3 appointment_checker.py False ")

pass








