import smtplib
import requests
from twilio.rest import Client
import os
import sched

twilio_phone = os.environ.get('TWILIO_PHONE')
astronomy_acct_id = os.environ.get('ASTRONOMY_ACCT_ID')
astronomy_api_key = os.environ.get('ASTRONOMY_API_KEY')


# Start with sunrise and sunset info - from askgeo.com's Astronomy database
# Add the chance of precipitation
# And the relative temp
# and an inspirational quote
# finish with a reminder of something you should do, enjoy, or pursue

lat_long_string = "47.7362712%2C-122.344438"
astronomy_api_url = "https://api.askgeo.com/v1/{}/{}/query.json?databases=Astronomy&points={}".format(astronomy_acct_id, astronomy_api_key, lat_long_string)

astronomy_json_response = requests.get(astronomy_api_url).json()

# info we care about
# data
#   0
#       Astronomy
#           TodaySunriseIso8601
#           TodaySunsetIso8601

astronomy_data = astronomy_json_response['data'][0]['Astronomy']
# print(str(astronomy_data))
sunrise_time = astronomy_data['TodaySunriseIso8601'][11:]
sunset_time = astronomy_data['TodaySunsetIso8601'][11:]

wake_the_day_message = "Good morning! Sunrise is at {}, sunset will be at {}. ".format(sunrise_time, sunset_time)

# Finding precipitation
wunderground_key = os.environ.get('WUNDERGROUND_API')
wunderground_url = "http://api.wunderground.com/api/{}/forecast/q/WA/Seattle.json".format(wunderground_key)
wunderground_response = requests.get(wunderground_url).json()

#data we're concerned with
# forecast:simpleforecast:forecastday:0:
# high, low, qpf_day:in (inches of precip), conditions
wunderground_response_data = wunderground_response['forecast']['simpleforecast']['forecastday'][0]

high_temp = wunderground_response_data['high']
low_temp = wunderground_response_data['low']
precip = wunderground_response_data['qpf_day']['in']
conditions = wunderground_response_data['conditions']

wake_the_day_message += "The high today will be {} and the weather will be {}".format(high_temp, conditions)

# Twilio usage
# import account secrets
twilio_id = os.environ.get('TWILIO_ID')
twilio_token = os.environ.get('TWILIO_TOKEN')

# instantiate the twilio client
sms_client = Client(twilio_id, twilio_token)

# send a message todo: figure out how to schedule. celery task queue? http://www.celeryproject.org/
new_message = sms_client.api.account.messages.create(to='+12064597793', from_=twilio_phone, body=wake_the_day_message)
