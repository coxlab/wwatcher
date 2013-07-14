#!/usr/bin/python

import sys
import pylab
import argparse
from spreadsheet import Spreadsheet

class WeightWatcher(object):

	def __init__(self, username, password, spreadsheet_name='Daily Weights after 7-11-13', \
			spreadsheet_url=None):
		'''
		
		
		'''
		
		#self.data is a list of lists with all the spreadsheet data
		#e.g. nested list ['date/time', 'username#coxlab.org', 'animal ID', 'weight', 'after water? yes or no'] <--one row
		self.data = Spreadsheet(username, password, spreadsheet_name, spreadsheet_url).worksheet_open.get_all_values()
		self.animals_to_analyze = []
		self.data_list_length = len(self.data)
	
	def IsHeavyEnough(self):
		#go through each aninmal specified by user and make sure it weighs at least 90% its latest max weight
		
		def find_max_weight(animal):
			
