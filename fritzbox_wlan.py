#!/srv/homeassistant/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import requests
import xml.etree.ElementTree as ET
import json
import sys
import time

def RequestLogin(response=None):
    url = 'http://fritz.box/login_sid.lua{}'.format('' if response is None else '?response={}'.format(response))

    request = requests.request('GET', url)
    root = ET.fromstring(request.content)
    SID = root.findall('SID')[0].text
    challenge = root.findall('Challenge')[0].text
    blocktime = root.findall('BlockTime')[0].text

    return SID, challenge, blocktime


def GetSessionID(password, response=None):
    SID, challenge, blocktime = RequestLogin()

    time.sleep(int(blocktime))

    if (SID == '0000000000000000'):
       	SID, _, _ = RequestLogin(u'{}-{}'.format(challenge, hashlib.md5('{}-{}'.format(challenge, password).encode('UTF-16LE')).hexdigest()))
	
    return SID


def main(argv):
    password = ''
    SSID = '' 

    SID = GetSessionID(password)	
    
    url = "http://fritz.box/data.lua"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {}

    if argv[1] == 'on':
        payload = {'xhr': '1', 'sid': SID, 'lang': 'de', 'no_sidrenew': '', 'apply': '', 'oldpage': '/wlan/wlan_settings.lua', 'active': 'on', 'SSID': SSID, 'hidden_ssid': 'on'}
    else:
        payload = {'xhr': '1', 'sid': SID, 'lang': 'de', 'no_sidrenew': '', 'apply': '', 'oldpage': '/wlan/wlan_settings.lua'}

    response = requests.request("POST", url, headers=headers, data=payload)

    
    requests.request('GET', 'http://fritz.box/login_sid.lua?logout=1&sid={}'.format(SID))

if __name__ == "__main__":
    main(sys.argv)
