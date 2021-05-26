import requests, hashlib
import json
import sys
from datetime import datetime
#brew install libffi cairo
#pip3 install cairosvg
from cairosvg import svg2png
import time
import random
import schedule
#pip3 install pyjwt
import jwt




availabilityCheckUrl="https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict"
baseUrl = "https://cdn-api.co-vin.in/api/v2/auth/public"
basePrivateUrl = "https://cdn-api.co-vin.in/api/v2"
getBeneficiariesUrl = "/appointment/beneficiaries"
bookingSlotUrl="/appointment/schedule"
generateOtpUrl="/generateOTP"
generateOtpPrivateUrl="/auth/generateMobileOTP"
confirmOtpPriavateUrl="/auth/validateMobileOtp"
confirmOtpPublicUrl="/confirmOTP"
generateCaptchaUrl="/auth/getRecaptcha"

authToken = ""
captcha = ""
preferred_center=""
preferred_vaccine=""
beneficiaries=[]
randomToken ="U2FsdGVkX1+TPSV7/E3PENx8ObiaQ9mIov/NO0Ry1mt5O8Awl1Ix+kX68wcBDbBTODj4Ejy3KkeW3n8ZqYhlqA=="

def generateOtp(phone_number):
    body = {"mobile":str(phone_number),"secret":randomToken}
    txnId=""
    res = requests.post(url=basePrivateUrl+generateOtpPrivateUrl,json=body,headers=authenticatedHeadr)
    print(res.status_code, res.text)
    if res.status_code == 200:
      response =  json.loads(res.text)
      txnId = response["txnId"]
      return txnId,True
    return txnId,False
pass

def confirmOtp(txnID,otp):
    hashed_otp = hashlib.sha256(otp.encode())
    body = {"txnId": txnID, "otp":hashed_otp.hexdigest()}
    print("otp is:",hashed_otp.hexdigest())
    res = requests.post(url=basePrivateUrl+confirmOtpPriavateUrl,json=body,headers=authenticatedHeadr)
    print(res.status_code, res.text)
    if res.status_code == 200:
      response =  json.loads(res.text)
      authToken = response["token"]
      return authToken,True
    else:
      print(res.status_code, res.reason)
    return authToken,False

pass

def get_beneficiaries(authenticatedHeadr):
    res = requests.get(url=basePrivateUrl+getBeneficiariesUrl,headers=authenticatedHeadr)
    print(res.status_code, res.text)
    if res.status_code == 200:
      response =  json.loads(res.text)
      beneficiaries = response["beneficiaries"]
      if len(beneficiaries) == 1 :
        beneficiariy_ids= [b["beneficiary_reference_id"] for b in beneficiaries]
        return beneficiariy_ids,True
      else :
        print("check the beneficiaries result and provide one beneficiary_reference_id")
        return [],False
    else:
      print(res.status_code, res.reason)
pass

def get_captcha(authenticatedHeadr):
    res = requests.post(url=basePrivateUrl+generateCaptchaUrl,json={},headers=authenticatedHeadr)
    print(res.status_code)
    if res.status_code == 200:
      response =  json.loads(res.text)
      captcha_svg = response["captcha"]
      convert_svg_to_png(captcha_svg)
      #save the file in png
      print(captcha_svg)
      print("captcha file saved at captcha.png, Open the file in any image viewer and provide the captcha. check read me for more details.")
      captcha = input ( "provide captch : ")
      return captcha,True
    print("error while getting captcha",res.text)
    return "",False


def convert_svg_to_png(svg_string):
    svg2png(bytestring=svg_string,write_to='captcha.png')
pass


def schedule_check_appointments(district_id_str, authenticatedHeadr,beneficiaries,captcha,decoded_token):
  #scheduling at random frequency between 1 to 5 seconds.
  time_span = random.randint(1, 5)
  schedule.clear()
  #print(f'Scheduled in {time_span} seconds',str(datetime.now()))
  schedule.every(time_span+0.2).seconds.do(check_and_book_appointments,district_id_str, authenticatedHeadr,beneficiaries,captcha,decoded_token)
pass

def check_and_book_appointments(district_id_str, authenticatedHeadr,beneficiaries,captcha,decoded_token):

  print("checking for appoitnment.","token will expire at :",str(datetime.fromtimestamp(decoded_token["exp"])))

  if  datetime.timestamp(datetime.now()) > decoded_token["exp"]:
      print("token as expired. Please re-run the script.")
      return False

  today_date = datetime.today().strftime("%d-%m-%Y")
  params= {"district_id":int(district_id_str),"date":datetime.today().strftime(today_date),"t":str(datetime.now())}
  response = requests.get(url=availabilityCheckUrl,params=params,headers=authenticatedHeadr)
  slot_booked = False
  if response.status_code != 200:
    print("error in fetching data.",response.status_code, response.content)

  else:
    contents = json.loads(response.content)
    centers=contents["centers"]
    #print("total centers are:",str(len(centers)))
    avaialble_centers=[]
    for c in centers:
      #there are multiple sessions i.e days for which appoints could be available.
      for session in c["sessions"]:
        if (session["min_age_limit"] == 18 and session["available_capacity_dose1"] > 0):
          center_name=c["name"]
          avaialble_centers.append((c,session))
      pass
    pass

    if len(avaialble_centers)>0:
      print("Available schedules :",avaialble_centers)
      slot_booked = book_slot(authenticatedHeadr,avaialble_centers,beneficiaries,captcha)
    pass

  #print("done")
  #print(".",end =" ",flush=True)
  if not slot_booked:
     schedule_check_appointments(district_id_str, authenticatedHeadr,beneficiaries,captcha,decoded_token)
  return schedule.CancelJob
pass

def book_slot(authenticatedHeadr,avaialble_centers,beneficiaries,captcha):

  for center,session in avaialble_centers:
      notification_message = build_notification_message(center,session)
      if (preferred_center !="" and center["center_id"] != preferred_center):
        print("skipping center which has ",notification_message)
        continue
      if preferred_vaccine !="" and session["vaccine"] != preferred_vaccine:
        print("Skipping center with non-matching vaccine : ",notification_message)
        continue
      is_booked,error_code,message = book_slot_at_center(center["center_id"],session["session_id"],captcha,beneficiaries,authenticatedHeadr)
      print (is_booked,error_code,message)
      return is_booked
  return False

def book_slot_at_center(center_id, session_id, captcha, beneficiaries,authenticatedHeadr):
    body = { "center_id":str(center_id),"session_id":str(session_id),"beneficiaries":beneficiaries,"slot":"09:00AM-11:00AM",
          "captcha":captcha,"dose":1
    }
    res = requests.post(url=basePrivateUrl+bookingSlotUrl,json=body,headers=authenticatedHeadr)
    print(res.status_code,res.text)
    if res.status_code == 200:
        return True,res.status_code, res.text

    return False, res.status_code, res.text
pass

def build_notification_message(center,session):
  message = "Avalaiblity for dose 1 at : "+center["name"]+", vaccine: "+str(session["vaccine"])+",pin code: "+str(center["pincode"])+", Slots: "+str(session["available_capacity_dose1"])+",center_id:"+str(center["center_id"])+", Address: " + center["address"]+"\n"
  return message

# district_id 118 is for gurgaon
# change the date to today's date


print("checking for appointment")

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

authenticatedHeadr = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9,de-AT;q=0.8,de;q=0.7',
  'cache-control': 'max-age=0',
  'authority': 'cdn-api.co-vin.in',
  'if-none-match': 'W/"70af-IG18Mu2z2MCbpqHXH1z9GP3y+WU"',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
  'sec-ch-ua-mobile': '?0',
  'sec-fetch-dest': 'document',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "cross-site",
  "referrer": "https://selfregistration.cowin.gov.in/",
  "origin": "https://selfregistration.cowin.gov.in",
  "content-type":"application/json",
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

def ask_for_otp():
  otp = ""
  while True:
    otp=input('Enter the OTP: ')
    if otp != "":
      return otp
  pass


def run(user_phone_number,beneficiaries,district_id_str,preferred_center,preferred_vaccine):
    txnId,status = generateOtp(user_phone_number)
    #txnId,status = "<existing transaction id>",True
    if not status:
      return

    token,status =  confirmOtp(txnId,ask_for_otp())
    #token,status="<add your bearer token here>",True
    if not status :
      return
    authenticatedHeadr["authorization"] = "Bearer "+ token
    #beneficiaries ,status = get_beneficiaries(authenticatedHeadr)
    #beneficiaries,status =["<your beneficiary id >"],True

    if not status :
      return

    decoded_token = jwt.decode(token,algorithms="HS256",options={"verify_signature": False})
    print("token will expire at : ",str(datetime.fromtimestamp(decoded_token["exp"])))

    captcha,status = get_captcha(authenticatedHeadr)
    #captcha,status = "<existing captcha>",True
    if not status :
      return

    check_and_book_appointments(district_id_str,authenticatedHeadr,beneficiaries,captcha,decoded_token)
    while True:
      schedule.run_pending()
      time.sleep(1)
    pass
    print("all done")
pass


if __name__ == "__main__":

    print("provide center and user details. Check readme for more details. you can also hardcode these in the run")
    district_id_str = input("provide district id : ")
    #district_id_str = "188"
    if district_id_str == "":
        district_id_str = "188" # using gurgaon as default
    preferred_center = input("preferred center id (press empty for any) :")
    preferred_vaccine_id = input("press 1 for covaxin or 2 for any :")
    preferred_vaccine_id = ""
    if preferred_vaccine_id == "1":
      preferred_vaccine = "COVAXIN"
      pass
    user_phone_number = input("registered phone number :")
    beneficiaries_id = input("Please provide your beneficiry id. This is the REF ID on your cowin dashboard page. :")
    beneficiaries = [beneficiaries_id]
    #user_phone_number = "<your hadcoded phone number>"
    run(user_phone_number,beneficiaries,district_id_str,preferred_center,preferred_vaccine)

pass








