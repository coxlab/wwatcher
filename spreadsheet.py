#!/usr/bin/python

import gspread

class Spreadsheet(object):

	'''
	An instance of this class uses the gspread package (https://github.com/burnash/gspread)
		to communicate with the Google Docs API. This opens the first worksheet in a spreadsheet 
		specified in __init__ (i.e. sheet1)

	'''

	def __init__(self, username, password, spreadsheet_name='Daily Weights after 7-11-13', spreadsheet_url=None):

		'''
		param username: A string, the user's Google Docs email (e.g. chapman@coxlab.org)

		param password: A string, the user's password for Google Docs

		param spreadsheet_name: A string, name of the spreadsheet from which you want data,
			as it appears in Google Docs (e.g. "Daily Weights after 7-11-13")

		param spreadsheet_url: A string, the url for a Google Docs spreadsheet if you want to use a different one

		'''
		
		self.login = gspread.login(username, password)

		if spreadsheet_url == None:
			self.worksheet_open = self.login.open(spreadsheet_name).sheet1
		else:
			self.worksheet_open = self.login.open_by_url(spreadsheet_url).sheet1






