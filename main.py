import requests
import json
from PIL import Image, ImageFont, ImageDraw
import os
from datetime import datetime
import sys
import time

def main():

    #time.sleep(5)
    now = datetime.now()
    print("Python3 script started at " + now.strftime("%Y-%m-%d %H:%M:%S"))
    sys.stdout.flush()

    Spotipo_Key = "TOKEN-SPOTIPO"
    Darksky_Key = "DARSKY-KEY"

    color1 = (46,170,220,255)
    color2 = (12,76,150,255)

    urlVoucher = 'https://wifi.YOUR-NET.us/s/1/api/voucher/create/'
    headersVoucher = {"Content-Type":"application/json", "Authentication-Token":Spotipo_Key}

    fontWiFiName = ImageFont.truetype("fonts/Raleway-Light.ttf", 100)
    fontPreVoucher = ImageFont.truetype("fonts/Raleway-Light.ttf", 100)
    fontVoucher = ImageFont.truetype("fonts/Raleway-Black.ttf", size=220)
    fontSSID = ImageFont.truetype("fonts/Raleway-Light.ttf", 130)
    fontError = ImageFont.truetype("fonts/Raleway-Light.ttf", 30)
    fontWeather1 = ImageFont.truetype("fonts/Raleway-Black.ttf", 40)
    fontWeather2 = ImageFont.truetype("fonts/Raleway-Light.ttf", 40)
    fontDate = ImageFont.truetype("fonts/Raleway-Black.ttf", 90)
    W, H = (1920, 1080)
    ssid = "SSID-NAME"

    urlWeather = 'https://api.darksky.net/forecast/' + Darksky_Key + '/16.225,-61.383?lang=fr&exclude=flags,alerts,hourly,minutely&units=si'

    while True:

        try:
            ## Voucher Code ##
            r = requests.post(urlVoucher, headers=headersVoucher, data = json.dumps({
               "duration_val": "4", ## 4 hours
			   "duration_type": "2",
			   "batchid": "4130",
               "number": "1",
               "num_devices": "10",
               "speed_dl": "1024",
               "speed_ul": "256",
               "bytes_t": "0"}))

            rJSON = json.loads(r.text)
            voucher = rJSON['data']['vouchers'][0]

            img = Image.open("images/background_PiSpot_HDMI-blanc.png")
            draw = ImageDraw.Draw(img)

            imgLogo = Image.open("images/logoGpconnect.png")
            imgLogo.load()
            backgroundLogo = Image.new("RGB", imgLogo.size, (255, 255, 255))
            backgroundLogo.paste(imgLogo, mask=imgLogo.split()[3])
            img.paste(backgroundLogo, (60,50))

            w, h = draw.textsize("WiFi: ", fontWiFiName)
            i, j = draw.textsize(ssid, fontSSID)
            draw.text(((W-i-w)/2 - 20,(H-h)/3.2), "WiFi: ", fill=color1, font=fontWiFiName)
            draw.text(((W-i+w)/2 + 20,(H-j)/3.2), ssid, fill=color1, font=fontSSID)

            w, h = draw.textsize("Voucher: ", fontPreVoucher)
            i, j = draw.textsize(voucher, fontVoucher)
            draw.text(((W-i-w)/2 - 20,(H-h)/2), "Voucher: ", fill=color2, font=fontPreVoucher)
            draw.text(((W-i+w)/2 + 20,(H-j)/2), voucher, fill=color2, font=fontVoucher)
            ## End Voucher Code ##

            ## Weather ##
            r = requests.get(urlWeather)
            rJSON = json.loads(r.text)

            currentIcon = rJSON["currently"]["icon"]
            currentTemp = round(rJSON["currently"]["temperature"])
            currentSummary = rJSON["currently"]["summary"]
            currentApparentTemp = round(rJSON["currently"]["apparentTemperature"])
            dailyMinimalTemp = round(rJSON["daily"]["data"][0]["temperatureLow"])
            dailyMaximalTemp = round(rJSON["daily"]["data"][0]["temperatureHigh"])
            dailySummary = rJSON["daily"]["data"][0]["summary"]

            imgDay = Image.open("images/" + currentIcon +".png")
            imgDay.load()
            background = Image.new("RGB", imgDay.size, (255, 255, 255))
            background.paste(imgDay, mask=imgDay.split()[3])
            img.paste(background, (350,750))

            draw.text((650,750), str(currentTemp) + "˚ - " + currentSummary, fill=color2, font=fontWeather1)
            draw.text((650,800), "Ressentie: " + str(currentApparentTemp) + "˚ Minimale: " + str(dailyMinimalTemp) + "˚ Maximale: " + str(dailyMaximalTemp) + "˚", fill=color2, font=fontWeather2)
            draw.text((650,850), dailySummary, fill=color2, font=fontWeather2)
            ## End Weather ##

            ## Date ##
            draw.text((1300,50), datetime.today().strftime("%d/%m/%Y"), fill=color2, font=fontDate)
            ## End Date

            img.save('images/current.png', "PNG")
            os.system("sudo killall -9 fbi")
            os.system("sudo /usr/bin/fbi -d /dev/fb0 -T 1 --noverbose -a images/current.png")

        except Exception as e:
            print(e)
            sys.stdout.flush()
            typeException = type(e).__name__
            img = Image.open("background_PiSpot_HDMI.png")
            draw = ImageDraw.Draw(img)
            w, h = draw.textsize(typeException, font=fontVoucher)
            draw.text(((W-w)/2,(H-h)/2), typeException, fill=(255,0,0,255), font=fontVoucher)
            img.save('images/error.png', "PNG")
            os.system("sudo killall -9 fbi")
            os.system("sudo /usr/bin/fbi -d /dev/fb0 -T 1 --noverbose -a images/error.png")
            time.sleep(60) ## 1 minute before trying again
            continue

        time.sleep(60*60) ## 1 hour for next voucher

if __name__ == "__main__":
    main()
