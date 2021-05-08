import requests
import json
from datetime import datetime
import schedule
import time
import random
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events


telegram_token='<telegram bot token>'
api_id='<telegram_app>'
api_hash='<telegram_app_hash>'
phone='<your phone number for verification>'

chat_id = "-1001448255643"
channel_name = 'test12xdsv'  #to which you want to send the message
already_notified={}

def sendNotification(tele_notifications):
  client = TelegramClient('session', api_id, api_hash)
  client.connect()
  if not client.is_user_authorized():

      client.send_code_request(phone)

      # signing in the client
      client.sign_in(phone, input('Enter the code: '))


  try:
      # sending message using telegram client
      entity=client.get_entity(channel_name)
      message=""
      for name,value in tele_notifications.items():
        center=value[0]
        message = message + "Avalaiblity at : "+name+", pin code: "+str(center["pincode"])+", Slots: "+str(value[1])+", Address: " + center["address"]+"\n"
      print("sending message:",message,str(datetime.now()))
      client.send_message(entity=entity, message=message)
  except Exception as e:

      # there may be many error coming in while like peer
      # error, wwrong access_hash, flood_error, etc
      print("error",e)

  # disconnecting the telegram session
  client.disconnect()


def schedule_check_appointments():
  #scheduling at random frequency.
  time_span = random.randint(1, 5)
  schedule.clear()
  print(f'Scheduled in {time_span} seconds',str(datetime.now()))
  schedule.every(time_span+0.2).seconds.do(check_appointments)
  while True:
    schedule.run_pending()
    time.sleep(1)
  pass

def check_appointments():
  response = requests.get(url=url,params=params,headers=headers)

  if response.status_code != 200:
    print("error in fetching data.",response.status_code, response.content)

  else:
    contents = json.loads(response.content)
    centers=contents["centers"]
    notifications={}
    for c in centers:
      #there are multiple sessions i.e days for which appoints could be available. TODO: to send different notification message for each date.
      for session in c["sessions"]:
        if (session["min_age_limit"] >= 18 and session["available_capacity"] >1 ):  # no point of sending notification with 1 slot as it will get filled
          center_name=c["name"]
          try:
            #ignore already notified centers to avoid flood of notifications
            data=already_notified[center_name]
          except KeyError:
            notifications[center_name]=(c,session["available_capacity"])
            already_notified[center_name]=True
          break
      if len(notifications)>0:
        break

    #if len(notifications)>0:
      #sendNotification(notifications)

  print("done")
  schedule_check_appointments()
  return schedule.CancelJob


# district_id 118 is for gurgaon
# change the date to today's date
params= {"district_id":188,"date":"08-05-2021"}

print("checking for appointment")

url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict"

print(url)

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


#schedlung the job
schedule_check_appointments()








