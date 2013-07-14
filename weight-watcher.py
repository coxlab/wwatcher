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
	
	def IsHeavyEnough(self, self.animals_to_analyze):
		'''
		#go through last 4 weekday weights of each aninmal specified by user and make sure each day it weighs at least 90 
		percent its most recent max weight

		param self.animals_to_analyze should be a list of strings

		*Returns a dict with animal names (str) as keys and True as the value iff each of the last 4 weekdays 
		it weighed enough*
		'''

		#================================================================================================================

		#get latest max weights from backwards spreadsheet (backwards so it starts looking for most recent data)
		#make dictionary to store animal names as keys and max weights as values
		#use data_position to remember where you are in the backwards (i.e. most recent) weights data during while loop
		maxes = {}
		animals_copy = self.animals_to_analyze[:]
		data_position = 0
		backwards_data = self.data[::-1]
		#do the following until we've gotten every animal's max weight
		#backwards_data[data_position[5] is overnight h20 column, "yes" means the comp has found a max weight
		#backwards_data[data_position][3] is animal ID in the spreadsheet, so the first boolean makes sure it's an animal 
		#for which the user wants to verify the weight
		while (len(animals_copy)) > 0 and (data_position <= self.data_list_length):
			if (backwards_data[data_position][3] in animals_copy) and ("yes" in backwards_data[data_position][5]):
				#make sure there's an animal weight (not '-' or 'x' in position backwards_data[data_pos][4]
				#by trying to make the string an int; if there's an exception it's not a valid animal weight
				try:
					animal_weight = int(backwards_data[data_position][4])
					#if no exception, add key (animal ID as string) and value (weight as int) to maxes dict
					maxes[backwards_data[data_position][3]] = animal_weight
					animals_copy.remove(backwards_data[data_position][3])
					data_position += 1
				except ValueError:
					#continue in loop to find a weekend ("yes") weight with a proper numerical value
					data_position += 1

		print 'Found max weights: ' + str(maxes)
		#make sure all animal max weights were found
		if len(animals_copy) > 0:
			raise Exception("Could not find max weight for: " + str(animals_copy).strip('[]'))

		#================================================================================================================

		#get most recent 4 weekday weights for each animal
		#make mins dict to store animal ID (str) as keys and 4 weekday weights as values (a list of ints)
		def DaysNeeded():
			'''
			Returns a dict with a starting value of 4 (int) for each animal key (str) in animals_copy
			Used in the while loop below to make it keep looping until each animal has at least 4 weekday weights 
			'''
			days_status = {}
			for each in animals_copy:
				days_status[each] = 4
			return days_status

		animals_copy = self.animals_to_analyze[:]
		countdown = DaysNeeded()
		weekday_weights = {}
		data_position = 0

		while 









