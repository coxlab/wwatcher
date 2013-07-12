#!/usr/bin/python

import gdata.spreadsheet.service
import sys
import pylab
import argparse

class WeightWatcher(object):

	def __init__(self, username, password):
		'''
		Takes in 2 strings: username and password for Google Docs
		
		'''
		#use gdata API to access Google Docs
		self.client = gdata.spreadsheet.service.SpreadsheetsService()
		self.client.email = username
		self.client.password = password
		#self.client.source is the document ID for the shared spreadsheet "Animal Weights after 7-11-13"
		self.client.source = '0Artit3NRL1oDdFVWRFMyeWpRb005WWsxRjBvQXkteGc'
		
