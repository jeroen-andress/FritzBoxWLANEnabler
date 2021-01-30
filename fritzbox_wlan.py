#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import requests
import xml.etree.ElementTree as ET
import json
import sys
import time
import getpass

# to edit:
hostname = 'http://fritz.box'
password = getpass.getpass()
SSID = '' 

def RequestLogin(response=None):
    url = '{}/login_sid.lua{}'.format(hostname, '' if response is None else '?response={}'.format(response))

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
    SID = GetSessionID(password)	
    
    url = '{}/data.lua'.format(hostname)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'xhr': '1', 'sid': SID, 'lang': 'de', 'no_sidrenew': '', 'apply': '', 'oldpage': '/wlan/wlan_settings.lua'}

    if argv[1] == 'on':
        payload.update({'active': 'on', 'SSID': SSID, 'hidden_ssid': 'on'})

    response = requests.request("POST", url, headers=headers, data=payload)
    
    requests.request('GET', '{}/login_sid.lua?logout=1&sid={}'.format(hostname, SID))

if __name__ == "__main__":
    main(sys.argv)
