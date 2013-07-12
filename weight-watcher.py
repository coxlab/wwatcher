#!/usr/bin/python

import gdata.spreadsheet.service
import sys
import pylab
import argparse

class WeightWatcher(object):
	def __init__(self, username, password):
		self.client = gdata.spreadsheet.service.SpreadsheetsService()
		self.client.email = username
		self.client.password = password
		self.client.source = '0Artit3NRL1oDdFVWRFMyeWpRb005WWsxRjBvQXkteGc'
		
