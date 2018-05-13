# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
import pprint
from urllib.parse import parse_qs
import webbrowser
import pickle
from datetime import datetime, timedelta
import vk
import time
import urllib
import pathlib
import shutil

# id of vk.com application
APP_ID = 5977197
# file, where auth data is saved
AUTH_FILE = '.auth_data'
# chars to exclude from filename
FORBIDDEN_CHARS = '/\\\?%*:|"<>!'


def get_saved_auth_params():
	access_token = None
	user_id = None
	try:
		with open(AUTH_FILE, 'rb') as pkl_file:
			token = pickle.load(pkl_file)
			expires = pickle.load(pkl_file)
			uid = pickle.load(pkl_file)
		if datetime.now() < expires:
			access_token = token
			user_id = uid
	except IOError:
		pass
	return access_token, user_id


def save_auth_params(access_token, expires_in, user_id):
	expires = datetime.now() + timedelta(seconds=int(expires_in))
	with open(AUTH_FILE, 'wb') as output:
		pickle.dump(access_token, output)
		pickle.dump(expires, output)
		pickle.dump(user_id, output)
		print("Token is saved")


def get_auth_params():
	auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
				"&scope=wall,messages,photos&redirect_uri=http://oauth.vk.com/blank.html"
				"&display=page&response_type=token".format(app_id=APP_ID))
	webbrowser.open_new_tab(auth_url)
	redirected_url = input("Paste here url you were redirected:\n")
	aup = parse_qs(redirected_url)
	aup['access_token'] = aup.pop('https://oauth.vk.com/blank.html#access_token')
	save_auth_params(aup['access_token'][0], aup['expires_in'][0], aup['user_id'][0])
	return aup['access_token'][0], aup['user_id'][0]


def get_api(access_token):
	session = vk.Session(access_token=access_token)
	return vk.API(session)


def main():
	file_num = 0
	START_FROM = '0'
	CONVERSATION_ID = '137019345'
	MEDIA_TYPE = 'photo'

	access_token, _ = get_saved_auth_params()
	if not access_token or not _:
		access_token, _ = get_auth_params()
	vkapi = get_api(access_token)

	content = vkapi.messages.getHistoryAttachments(peer_id = CONVERSATION_ID, media_type = MEDIA_TYPE, start_from = START_FROM, count = 30, photo_sizes = 0, v = 3.0)
	pathlib.Path(CONVERSATION_ID).mkdir(parents=True, exist_ok=True) 
		
	while content.get('next_from') is not None:
		content_number = len(content)-2
		content_numberT = content_number + 1
		while content_number != 0:	
			Number = len(content[str(content_numberT - content_number)]['photo'])
			if Number == 14:
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src_xxxbig','0')))		
			elif Number == 13: 
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src_xxbig','0')))
			elif Number == 12: 
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src_xbig','0')))
			elif Number == 11: 
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src_big','0')))
			elif Number == 10:
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src','0')))
			elif Number == 9: 
				href = (str(content[str(content_numberT - content_number)]['photo'].get('src_small','0')))					
			if href != '0':
				name = str(CONVERSATION_ID) + '_' + str(file_num) + ".jpg"
				urllib.request.urlretrieve(href, CONVERSATION_ID + '\\' + name)
				file_num+=1
				print(name + " saved")
			content_number-=1
			
		START_FROM = str(content.get('next_from'))
		content = vkapi.messages.getHistoryAttachments(peer_id = CONVERSATION_ID, media_type = MEDIA_TYPE, start_from = START_FROM, count = 30, photo_sizes = 0, v = 3.0)	
		
main()