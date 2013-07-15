#!/usr/bin/python

import gspread
import sys
import pylab
import argparse

class Spreadsheet(object):

	'''
	An instance of this class uses the gspread package (https://github.com/burnash/gspread)
		to communicate with the Google Docs API. This opens the first worksheet in a spreadsheet 
		specified in __init__ (i.e. sheet1 in 'Daily Weights after 7-11-13')

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

class WeightWatcher(object):

	def __init__(self, username, password, animals, spreadsheet_name='Daily Weights after 7-11-13', \
			spreadsheet_url=None):
		'''
		An instance of the WeightWatcher class has a spreadsheet class attribute to 
			access Google Sheets data with animal weights. The WeightWatcher class 
			also has methods to monitor and analyze animal weights.

		param username: a string, login email for Google Docs
		param password: a string, login password for Google Docs
		param animals: a list, where each item in the list is an animal ID (str)
		param spreadsheet_name (optional): a string, Name of spreadsheet you want to parse, 
			default is currently the Cox lab shared sheet 'Daily Weights after 7-11-13'
		param spreadsheet_url (optional): a string, url for a spreadsheet if you want to 
			use this instead of a sheet name or the default spreadsheet_name
		'''
		
		#self.data is a list of lists with all the spreadsheet data
		#e.g. nested list ['date/time', 'username#coxlab.org', 'animal ID', 'weight', 'after water? yes or no'] <--one row from spreadsheet
		self.data = Spreadsheet(username, password, spreadsheet_name, spreadsheet_url).worksheet_open.get_all_values()
		self.animals_to_analyze = animals
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
		while (len(animals_copy)) > 0 and (data_position < self.data_list_length):
			if (backwards_data[data_position][3] in animals_copy) and ("yes" in backwards_data[data_position][5]):
				#make sure there's an animal weight (not '-' or 'x' in position backwards_data[data_pos][4]
				#by trying to make the string an int; if there's an exception it's not a valid animal weight
				try:
					animal_weight = int(backwards_data[data_position][4])
					#if no exception, add key (animal ID as string) and value (weight as int) to maxes dict
					maxes[backwards_data[data_position][3]] = animal_weight
					animals_copy.remove(backwards_data[data_position][3])
				except ValueError:
					print "ValueError at %s" % data_position
			data_position += 1

		print 'Found max weights: ' + str(maxes)
		#make sure all animal max weights were found
		if len(animals_copy) > 0:
			raise Exception("Could not find max weight for: " + str(animals_copy).strip('[]'))

		#================================================================================================================

		#get most recent 4 weekday weights for each animal
		#make mins dict to store animal ID (str) as keys and 4 weekday weights as values (a list of ints)
		def DaysNeeded(animals_copy):
			'''
			Returns a dict with a starting value of 4 (int) for each animal ID key (str) in animals_copy
			Used in the while loop below to make it keep looping until each animal has at least 4 weekday weights 
			'''
			days_status = {}
			for each in animals_copy:
				days_status[each] = 4
			return days_status

		def AllDaysRetrieved(DaysNeededDict):
			'''
			Returns a boolean to indicate whether EVERY animal has 4 weekday weights recorded, indicated by a value of 0 
			in countdown
			'''
			dict_values = DaysNeededDict.values()
			for each in dict_values:
				if each > 0:
					return False
			return True

		def MakeDictLists(animals_copy):
			'''
			make an empty list as the value for each animal (key) in weekday_weights 
			'''
			dictionary = {}
			for each in animals_copy:
				dictionary[each]: []
			return dictionary

		animals_copy = self.animals_to_analyze[:]
		countdown = DaysNeeded(animals_copy)
		weekday_weights = MakeDictLists(animals_copy)
		data_position = 0
		#check to see if every animal has 4 weekday weights before continuing in the while loop
		while not (AllDaysRetrieved(countdown)) and (data_position < self.data_list_length):
			#do the following if the data position (row) is for an animal in self.animals_to_analyze and it's 
			#a weekday weight (i.e. "no" in column 5 of the spreadsheet)
			if (backwards_data[data_position][3] in animals_copy) and ("no" in backwards_data[data_position][5]):
				try:
					animal_weight = int(backwards_data[data_position][4])
					if countdown[backwards_data[data_position][3]] > 0:
						weekday_weights[backwards_data[data_position][3]].append(animal_weight)
						countdown[backwards_data[data_position][3]] -= 1
				except ValueError:
					print "ValueError at %s" % data_position
			data_position += 1

		print "Found weekday weights: " + str(weekday_weights)
		if not AllDaysRetrieved(countdown):
			raise Exception("Could not find weekly weight for all animals")

		#================================================================================================================

		










