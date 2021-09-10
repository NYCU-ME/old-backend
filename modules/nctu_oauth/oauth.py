#-*- encoding: UTF-8 -*-

import requests

OAUTH_URL = 'https://id.nycu.edu.tw'

class Oauth(object):
	def __init__(self, redirect_uri, client_id, client_secret):
		self.grant_type = 'authorization_code'
		self.code = None
		self.client_id = client_id
		self.client_secret = client_secret
		self.redirect_uri = redirect_uri

	def get_code_url(self):
		return OAUTH_URL + '/o/authorize/?client_id=' + self.client_id + '&scope=profile&response_type=code'

	def get_token(self, code):
		self.code = code
		get_token_url = OAUTH_URL + '/o/token/'
		data = {
			'grant_type': 'authorization_code',
			'code': self.code,
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'redirect_uri': self.redirect_uri
		}
		result = requests.post(get_token_url, data=data)
		access_token = result.json().get('access_token', None)

		if access_token:
			return access_token

		return False

	def get_profile(self, token):

		headers = {
			'Authorization': 'Bearer ' + token
		}
		get_profile_url = OAUTH_URL + '/api/profile/'

		data = requests.get(get_profile_url, headers=headers).json()

		return data
