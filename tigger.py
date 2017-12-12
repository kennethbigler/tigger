#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TODO: Set up auto deploy (Erik)

import os
from bottle import get, post, run, request
import requests
import json
import multiprocessing
import time

# This method is used for:
#    - retrieving message text, when the webhook is triggered with a message
#    - Getting the username of the person who posted the message if a command is recognized
def sendSparkGET(url):
    print("Run: sendSparkGet")
    response = requests.get(
        url,
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + bearer
        }
    )
    response.raise_for_status()
    return response.json()

# This method is used for:
#    - posting a message to the Spark room to confirm that a command was received and processed
def sendSparkPOST(url, data):
    print("Run sendSparkPost")
    response = requests.post(
        url,
        data=json.dumps(data),
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + bearer
        }
    )
    response.raise_for_status()
    return response.json()

def sendSparkMsg(_type, pkg):
    data = {"roomId": webhook['data']['roomId']}
    data[_type] = pkg
    sendSparkPOST("https://api.ciscospark.com/v1/messages", data)

def spammer():
	for i in range(15):
		sendSparkMsg("text", "and they don't stop coming")
		time.sleep(1)
	else:
		sendSparkMsg("text", "Way to go, you almost broke me.")

qtest = None

# triggers are in Conjunctive Normal Form (CNF)
# Ex: A ^ N ^ D ^ (O v R) === ["A", "N", "D", ["O", "R"]]
# to indicate not, use "!" as it's own element
# Ex: !A ^ (B v C) === ["!", "A", ["B", "C"]]
tiggerDictionary = [
    {
        "triggers": ["cancer"],
        "type": "text",
        "payload": "WARNING: This message contains chemicals known to the State of California to cause cancer and birth defects or other reproductive harm."
    },
    {
        "triggers": [["chuck", "chuckco"]],
        "type": "markdown",
        "payload": "# 𝓹𝓻𝓪𝓲𝓼𝓮 𝓫𝓮 𝓾𝓷𝓽𝓸 𝓱𝓲𝓶"
    },
    {
        "triggers": [["/not too", "not too", "jeans"]],
        "type": "files",
        "payload": ["https://lh3.googleusercontent.com/SEKZgteoZn6-_fNJLWET5gPybQOKdOkdJG4pvUq2umoTL8oLBBIzUMASm9MPMEeaPMGqURkNeZOc028FeiAU5fEivXST_64r0KoJKyDWYP4b4kWkR4MhXSvYq1lHNkP5g9AQb6DunyHCHGI0e1dts8mbtdgPV_KOBzi5ExAepzm7JHPALlOM054E6RNXXxziMiQQu0TbeUo2O4Nw29XWTfiEiFPcV3x67f0wTRFsmCWPdb7lucczI7aOZfCyZ49-A1fBOnLHG5GPKhebrZjULsYH3Ju5i9FHKIOSqoZ7f0i11jePcC_R7AKHYewC2BJWUTrRGevn8fh07vhhl9F_0JQlF2qoGHB2RGzwJdXWq8JwgGCu8RkiQnUXecuhO4KjjtzAfWa0fV22kD7ojT4YEIyEI6wE7e7Q9rTR6TY58Q_Zozkc5n6S8m8_RQ3NmQxuySPSXu9vp7KzmUJ3Pc12Exqnq-U9ELfUoPyH676pPm8qXM3N_jOswtPxNwz2nFK9GK6pbhsJmOZ3DLSbiioBjvbKtE7rh_n1Vs3yFkQDKhK1iPnNf5RrT96UjrXsYG163l8DbFhZjaltOcBPxWZ8do0aTmfmgiVJ2fatuFP6xx5Nlw-VDjZNHxPI9u2hXLgcDa4PhRHBcaNG43cNHa34ocy2Tr240ItCmmD9VMVGJn8=w478-h592-no"]
    },
    {
        "triggers": ["waste", "time"],
        "type": "files",
        "payload": ["http://i3.kym-cdn.com/photos/images/original/000/897/738/706.png"]
    },
    {
        "triggers": ["be humble"],
        "type": "text",
        "payload": "Sit down"
    },
    {
        "triggers": ["sit down"],
        "type": "text",
        "payload": "Be humble (lil bitch)"
    },
    {
        "triggers": ["fake news"],
        "type": "text",
        "payload": "WRONG!"
    },
    {
        "triggers": ["wrong"],
        "type": "text",
        "payload": "Fake news"
    },
    {
        "triggers": ["cisco", "!", ".com"],
        "type": "text",
        "payload": ".:|:.:|:. Chuck Co .:|:.:|:."
    },
    {
        "triggers": ["bug"],
        "type": "files",
        "payload": ["https://lh3.googleusercontent.com/xScm_RRPDSzEkPrwymbufoMAzdbineiebFfAyAHParC2KpzntnrP41s8Gjs69GfWkgCaldnMm9TW6LxonYEbG77Duehy_8VjtazihtpAmdKLkm4euKg5v4-5OpbslYV1wMS2gJo=w287-h375-no"]
    },
    {
        "triggers": ["steam", "ham"],
        "type": "files",
        "payload": ["https://lh3.googleusercontent.com/Ny4Icxd61yz42TXlWEdnEsVwUfs03bWSFQS_GSsl2t-SYldp5ITlFeNW7n1NdhW8ELniUwp04VbWeTIOOFvnv0_vH7gWVoD8wAZhc2hh5YiIoK9L1avYR1geOI1JG2L09DfX7mDZh4UYyGSHxywxJcUCPl8t5XxhDoJnaQEasQpKgS-sAcvy_nFM6RYkUciHrlJ2URfq1RQmu5r7COFDQGARsjO6wgmxnYrM5t-C9O-3QFyLV3i5ukuTSM1nfgNSJfIzP2hfeto2uBy4Nx78msIfY6ZOaKJDVbIV0mJ2FgGW_3np1sM2vFmVbmM_4Qzh75dZCld9nrcTUygzm0mrWJmeYnV3uJi7PhQ2W6C4U-K3csdzLkWRC8lpftkTSPgTGbTUGGbVrA-u53ah-mgJ8jWbfR6MTSQ3WHyD6UGSDQkUXM9Dq1GAgz1tf3rd50giTWr7eMo9pZUQvAA22nlM8lcnmaiehzSn2BugHsxZP7yfVqMWeCBlrt3L59PXXpvo2MQTKeh92iZS4C9SVNIoYzodM7NIaaP0hON1pRza4gNwwT6PK-Bwyef2znq0Q6twF8PT4M599Mfd5HWsIDROQyiM7oVx6rpOCOJrroSl-vFfab47lFwXJfkC6-Bxffokp2osqZLFjWJ5sUyx_veNhRTH4MVjCgw-M6v3wtHQJfk=w261-h141-no"]
    },
    {
        "triggers": ["children"],
        "type": "files",
        "payload": ["https://lh3.googleusercontent.com/dNs-YgduU2QBAgI8bI-NTHxdb76IjQgTMAurbA5kJj3crlkvDupSzc8tk8Z-_ci5BfdEjVaGVbuvMTMyLhaPIAh0PyWdYLsP06ZOsbV0rWdJ6bHOEo59jZSshheXBde6ZbzP_QDimKa7Rvbd_KTdh7olqLsDWE0WNO5egk5wmNLKb9uErhYn8whRR2sJzDUp8cjtCZPcw7CtjUBnu0tsTq0WbmbDCqU_VkJID0qLbiLtunQ46dHy9ZnhaKm8ftEJaKSsc6uF9YZuY9OjvLb0ZnN52niAywOFR6HbuqQRCEyQFY2QQ1WEyW1e_OHjD8WsNx1tr90hMyyJBa1pgY-ihkK-AC-18dgWqWsBUZwnVAUXCGVAlkfFyhUBHJZcH5pcH5YN_-oZy0TETnYDM80mIJPIPiBhsYurGZgvs3LyUyvSXn3LRulr5tKO0K_Pn8G1FQ_bKAV1A6DE5ovVwjgV-qY9oDHju78_t2Sx8i1FHpmyZkzDVwvuORoXYSOqdCz0g6WCAgjpnPGOAhrW_ZXEM7-X-8l2-7vsrZZxeV4T3AAZp3aJDuvmDsrPb0LxutJNuEk5X9L2jVE0XxOlKQbSYYaLe8RYBCTJbw57P0XOx7ykqWqr9QDhQYu8Uokiax8Mt9c9rowD8N7qleHpNEOTOILfv6BqundAZKkG_3w54Gs=w106-h100-no"]
    },
    {
        "triggers": [["fuck yea", "trashdove", "hell yea"]],
        "type": "files",
        "payload": ["http://i.imgur.com/50wBJit.gif"]
    },
    {
        "triggers": ["good shit"],
        "type": "markdown",
        "payload": "# 👌👀👌👀👌👀👌👀👌👀 good shit go౦ԁ sHit👌 thats ✔ some good👌👌shit right👌👌there👌👌👌 right✔there ✔✔if i do ƽaү so my self 💯 i say so 💯 thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ💯 👌👌 👌НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ👌 👌👌 👌 💯 👌 👀 👀 👀 👌👌"
    },
    {
        "triggers": ["understood"],
        "type": "files",
        "payload": ["https://lh3.googleusercontent.com/hJlIRL8tQD9lG-x82xY3E5VW7hTEWd63MGnuSRASTdxSld3wzk3tGK_6BPp-F6U5z0HASxxCPKUNmoGnnTcBGTlVQ9nPIwDB5R4XQfIKna43SE8ac_C4_lZK3qedzTyxNDE0vPsyBGQvSPmiodb7ExScPJVp23PCe-UyRc3ZmVQtTVTLtcVFceINjw4w3Y3ydpoystUljD-6CJECx8ez2wkU1L0i2eDJZhlG256VmAO09nYO5WaRg3hft_6rk-lFkg45RJmWTfbwUMN5k4hb7S6gTkzlf59Xj1ZXStjqd-fOVLjyb1yRhoSEwtDz0vus0FDaMymED8mbnJ51QFJZ5H58caOTnuDD0H0BkltdHU_xupvwcg-ZwzyUpvAwP_YqGLwA19ziOeVsKda4qXAiYndzsX-WPAAIVdmhr9X8Xvhz4Oo8r7FoH5c-0ThONMkJMmwhS2_sWdpdG6QCvQS5U1tYkOKlo8hXKi_mLKJUBtYQqQLJ4F9GaAlOw8FBiHKyTGv0lsdUEb8OzB5pfK0qfq1yarNWKEw7Puhl6GPDx9ZKcZSH99abgWnqvpTgmjZGjITRL0R_ZVr49veilDH2viLsKFQ6yy79zdn6GyG8CdEx_bpDEFcGTGl-g0ijSxdGC0LO0aEAK0_ThfZcPjws96_01A9jEAJZ8c4bvd6BK-M=w1200-h675-no"]
    },
    {
        "triggers": ["allahu", "!", "akbar"],
        "type": "text",
        "payload": "akbar"
    },
    {
        "triggers": ["allahu", "!", "akbar"],
        "type": "text",
        "payload": "akbar"
    },
    {
        "triggers": ["aloha", "!", "snackbar"],
        "type": "text",
        "payload": "snackbar"
    },
    {
        "triggers": ["please", "clap"],
        "type": "files",
        "payload": ["https://media.giphy.com/media/l0NwPo3VHujpJDI4w/giphy.gif"]
    },
    {
        "triggers": ["cash me outside"],
        "type": "files",
        "payload": ["https://media.giphy.com/media/26gIOEsGb5mcTiQEw/giphy.gif"]
    },
    {
        "triggers": ["jabbascript"],
        "type": "files",
        "payload": ["http://churchm.ag/wp-content/uploads/2011/01/jabbascript.jpg"]
    },
    {
        "triggers": ["git gud"],
        "type": "files",
        "payload": ["https://i.imgur.com/QdCdfmD.gif"]
    },
    {
        "triggers": ["nani"],
        "type": "files",
        "payload": ["https://i.ytimg.com/vi/U_0eocL8aGA/maxresdefault.jpg"]
    },
    {
        "triggers": ["backdoor"],
        "type": "files",
        "payload": ["https://i.imgur.com/bgwbje5.gif"]
    },
    {
        "triggers": ["good bot"],
        "type": "text",
        "payload": "Fuck you!"
    },
    {
        "triggers": ["triggersed"],
        "type": "text",
        "payload": "T-I-DOUBLE-G-ER-ED!"
    },
    {
        "triggers": ["hyperlul"],
        "type": "files",
        "payload": ["https://i.imgur.com/Yf8JBm5.gif"]
    },
    {
        "triggers": ["huehuehue"],
        "type": "files",
        "payload": ["https://i.imgur.com/rSZf8E7.gif"]
    },
    {
        "triggers": [["tigger", "t-i-double-g-er"]],
        "type": "text",
        "payload": "That's me!"
    },
    {
        "triggers": ["rude"],
        "type": "text",
        "payload": "Rude!"
    }
]

# evaluate OR logic of CNF input
def getOr(arr, message):
    flag = False

    for x in arr:
        # set not flag
        if (x == "!"):
            flag = True
            continue
        elif flag == False:
            # check if trigger is missing
            if x in message:
                return True
        # !(check if trigger is missing)
        elif x not in message:
            return True
        # reset flag
        flag = False
    return False

# evaluate AND (then total) logic of CNF input
def evalTrigger(arr, message):
    flag = False

    for trigger in arr:
        # set not flag
        if (trigger == "!"):
            flag = True
            continue
        # check if OR array
        elif isinstance(trigger, list):
            if flag == False:
                # evaluate or array
                if not getOr(trigger, message):
                    return False
            # !(evaluate or array)
            elif getOr(trigger, message):
                return False
            # clear not flag
            flag = False
        # and case
        else:
            if flag == False:
                # check if trigger is missing
                if trigger not in message:
                    return False
            # !(check if trigger is missing)
            elif trigger in message:
                return False
            flag = False

# generate helptext from dictionary
def generateHelpText():
    helptext = "type '/help' to see this text\nwell ^ [start coming v starts coming]\nplease stop\n"
    flag = False

    # iterate through dictionary
    for obj in tiggerDictionary:
        # iterate through triggers
        for trigger in obj.triggers:
            # set not flag
            if (trigger == "!"):
                flag = True
                continue
            # OR values
            elif isinstance(trigger, list):
                helptext += "![" if flag else "["
                flag = False
                for x in trigger:
                    if (trigger == "!"):
                        flag = True
                    else:
                        helptext += ("!" + x + ", ") if flag else (x + ", ")
                        flag = False
                helptext += "], "
            # AND values
            else:
                helptext += ("!" + trigger + ", ") if flag else (trigger + ", ")
                flag = False
        # add return between triggers
        helptext += "\n"

    return helptext

# Constants
bot_email = "tiggermepls@gmail.com"
bot_name = "Tigger Me"

bearer = os.environ.get('TIGGER_TOKEN')
if bearer == None:
    bearer = "ayylmao nicetry"

@post('/')
# When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
# using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
# further actions are taken. i.e.
def index():
    print("Run: index")
    global webhook
    webhook = request.json
    print(webhook['data']['id'])
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    global qtest
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')


        helptext = generateHelpText()

        # This is the location for basic commands
        if '/help' in in_message:
        	sendSparkMsg("text", helptext)
        # This is the location for text responses
        else:
            # test all triggers
            for obj in tiggerDictionary:
                if evalTrigger(obj.triggers, in_message):
                    sendSparkMsg(obj.type, obj.payload)
            # hasn't been migrated to object yet
            if 'well' in in_message and ('start coming' in in_message or 'starts coming' in in_message):
            	qtest = multiprocessing.Process(target=spammer)
            	qtest.start()
            	sendSparkMsg("text", "and they don't stop coming")
            if 'please stop' == in_message:
            	qtest.terminate()
            	sendSparkMsg("text", " :( ")

    return "true"

port = int(os.environ.get("PORT", 8069))
run(server='wsgiref', host='0.0.0.0', port=port)
