#!/usr/bin/env python

import gspread
import sys
import pylab
import argparse
import getpass
import datetime
import wwatcher
from matplotlib import pyplot
import matplotlib.dates
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
import random
from matplotlib import legend

def main():

	'''
	Parse command line options to analyze animal weight data from Google Sheets. Creates a WeightWatcher class and executes
	methods specified by the user on the command line. 
	'''
	#TODO add spreadsheet name and url customizability to command line interface
	parser = argparse.ArgumentParser(description="A command line tool to analyze animal weights stored in Google Sheets", \
		usage="wwatcher.py Username animalName1 animalName2 animalName3 [options] \n\
		or \n\
		wwatcher.py [options] Username animalName1 animalName2 animalName3")
	parser.add_argument('username', help="Google Docs username, required as first argument (e.g. chapman@coxlab.org)")
	parser.add_argument('animals', help="Animal IDs to analyze, separated by spaces. At least 1 is required, but you \
		can add as many as you want", nargs="+")
	parser.add_argument('-c', action="store_true", default=False, help="Check to make sure each animal weighed at least \
		90 percent of its most recent maximum (weekend) value for the last 4 weekdays")
	parser.add_argument('-d', help="Specify the number of weekdays to analyze with -c option")
	parser.add_argument('-g', action="store_true", default=False, help="Make a graph of each animal's weight over time")
	parser.add_argument('-a', action="store_true", default=False, help="Make one graph of every animal's weight over time")
	parser.add_argument('-r', action="store_true", default=False, help="Graph a linear regression where x values are max weights \
		and y values are the previous week's average daily weight")

	parsed = parser.parse_args()

	#make sure at least 1 specified option calls a WeightWatcher class method, else give the user help and exit
	if (parsed.c == False) and (parsed.g == False) and (parsed.a == False) and (parsed.r == False):
		parser.print_help()
		sys.exit()

	username = parsed.username
	animals = parsed.animals

	#if the username is weights@coxlab.org, no need to ask for password in terminal. It's this crazy string, and we want to run
	#the script automatically without stopping for user input every week
	if username == "weights@coxlab.org":
		password = "}ONCuD*Xh$LNN8ni;0P_HR_cIy|Q5p"
	else:
		password = getpass.getpass("Enter your Google Docs password: ")

	watcher = wwatcher.WeightWatcher(username, password, animals)
	#if the user selects the -c option, check animal weights to make sure they don't go below 90% max
	if parsed.c:
		if parsed.d:
			HeavyEnoughDict = watcher.IsHeavyEnough(days=parsed.d)
		else:
			HeavyEnoughDict = watcher.IsHeavyEnough()

		#make a list of animals that aren't heavy enough
		problem_animals = []
		for animal in animals:
			if not HeavyEnoughDict[animal]:
				problem_animals.append(animal)
		#TODO implement email functionality for alerts when this option is run automatically
		if len(problem_animals) == 0:
			print "Animal weights look fine. Awesome!\n"
		else:
			for each in problem_animals:
				print "A stupid algorithm thinks %s is underweight. You might want to check on him!" % each

	if parsed.g:

		#dict with animals ID strings as keys and a list of lists of the same length [[dates], [weights for those dates], [whether it was a weekend weight Boolean]]
		data_for_graph = watcher.format_data_for_graph()
		for animal in animals:
			dates = data_for_graph[animal][0]
			weights = data_for_graph[animal][1]
			fig = pyplot.figure(str(datetime.date.today()))
			pyplot.title("Animal weight over time")
			pyplot.ylabel("Animal Weight (g)")
			ax = fig.gca()
			mondays = WeekdayLocator(MONDAY, interval=2)
			alldays = DayLocator()
			weekFormatter = DateFormatter('%b %d %y')
			ax.xaxis.set_major_locator(mondays)
			ax.xaxis.set_minor_locator(alldays)
			ax.xaxis.set_major_formatter(weekFormatter)
			r = lambda: random.randint(0,255)
			ax.plot_date(matplotlib.dates.date2num(dates), weights, '#%02X%02X%02X' % (r(),r(),r()), lw=2, label=str(animal))
			pyplot.axis(ymin=400, ymax=750)
			ax.legend(loc='best')
			ax.xaxis_date()
			ax.autoscale_view()
			pyplot.setp(fig.gca().get_xticklabels(), rotation=35, horizontalalignment='right')
			pyplot.show()

	if parsed.a:

		#dict with animals ID strings as keys and a list of lists of the same length [[dates], [weights for those dates], [whether it was a weekend weight Boolean]]
		data_for_graph = watcher.format_data_for_graph()
		for animal in animals:
			dates = data_for_graph[animal][0]
			weights = data_for_graph[animal][1]
			fig = pyplot.figure(str(datetime.date.today()))
			pyplot.title("Animal weight over time")
			pyplot.ylabel("Animal Weight (g)")
			ax = fig.gca()
			mondays = WeekdayLocator(MONDAY, interval=2)
			alldays = DayLocator()
			weekFormatter = DateFormatter('%b %d %y')
			ax.xaxis.set_major_locator(mondays)
			ax.xaxis.set_minor_locator(alldays)
			ax.xaxis.set_major_formatter(weekFormatter)
			r = lambda: random.randint(0,255)
			ax.plot_date(matplotlib.dates.date2num(dates), weights, '#%02X%02X%02X' % (r(),r(),r()), lw=2, label=str(animal))
			pyplot.axis(ymin=400, ymax=750)
			ax.legend(loc='best')
			ax.xaxis_date()
			ax.autoscale_view()
			pyplot.setp(fig.gca().get_xticklabels(), rotation=35, horizontalalignment='right')
		pyplot.show()

	if parsed.r:

		data_for_graph = watcher.regression()
		fitted = pylab.polyfit(data_for_graph[0], data_for_graph[1], 1)
		line = pylab.polyval(fitted, data_for_graph[0])
		pylab.plot(data_for_graph[0], line)
		pylab.scatter(data_for_graph[0], data_for_graph[1])
		pylab.xlabel('Weekend (max) weight')
		pylab.ylabel('Avg Weekday Weight')
		pylab.show()

if __name__ == '__main__':
	main()

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
		print "\nLogging into Google Docs..."
		self.login = gspread.login(username, password)
		print "Importing spreadsheet from Google Docs..."
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
		#e.g. nested list ['date/time', 'username@coxlab.org', 'animal ID', 'weight', 'after water? yes or no'] <--one row from spreadsheet
	
		self.data = Spreadsheet(username, password, spreadsheet_name, spreadsheet_url).worksheet_open.get_all_values()
		print "Successfully imported spreadsheet\n"
		self.animals_to_analyze = animals
		self.data_list_length = len(self.data)
	
	def IsHeavyEnough(self, days=4):
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
		#backwards_data[data_position[4] is overnight h20 column, "yes" means the comp has found a max weight
		#backwards_data[data_position][2] is animal ID in the spreadsheet, so the first boolean makes sure it's an animal 
		#for which the user wants to verify the weight

		while (len(animals_copy)) > 0 and (data_position < self.data_list_length):
			if (backwards_data[data_position][2] in animals_copy) and ("yes" in backwards_data[data_position][4]):
				#make sure there's an animal weight (not '-' or 'x' in position backwards_data[data_pos][4]
				#by trying to make the string an int; if there's an exception it's not a valid animal weight
				try:
					animal_weight = int(backwards_data[data_position][3])
					#if no exception, add key (animal ID as string) and value (weight as int) to maxes dict
					maxes[backwards_data[data_position][2]] = animal_weight
					animals_copy.remove(backwards_data[data_position][2])
				except ValueError:
					pass #print "ValueError at %s, skipping to next cell" % data_position (used for testing)
			data_position += 1
			

		print '\nMax weights: ' + str(maxes) + "\n"
		#make sure all animal max weights were found
		if len(animals_copy) > 0:
			raise Exception("Could not find max weight for: " + str(animals_copy).strip('[]'))

		#================================================================================================================

		#get most recent 4 weekday weights for each animal
		#make mins dict to store animal ID (str) as keys and 4 weekday weights as values (a list of ints)
		def DaysNeeded(animals_copy, days):
			'''
			Returns a dict with a starting value of days (4 default) (int) for each animal ID key (str) in animals_copy
			Used in the while loop below to make it keep looping until each animal has at least 4 weekday weights 
			'''
			days_status = {}
			for each in animals_copy:
				days_status[each] = days
			return days_status

		def AllDaysRetrieved(DaysNeededDic):
			'''
			Returns a boolean to indicate whether EVERY animal has 4 weekday weights recorded, indicated by a value of 0 
			in countdown
			'''
			dict_values = DaysNeededDic.values()
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
				dictionary[each] = []
			return dictionary

		animals_copy = self.animals_to_analyze[:]
		#default number of days (4) used below "DaysNeeded(animals_copy, days) specified in WeightWatcher.IsHeavyEnough attributes
		countdown = DaysNeeded(animals_copy, days)
		weekday_weights = MakeDictLists(animals_copy)
		data_position = 0
		#check to see if every animal has 4 weekday weights before continuing in the while loop
		while not (AllDaysRetrieved(countdown)) and (data_position < self.data_list_length):
			#do the following if the data position (row) is for an animal in self.animals_to_analyze and it's 
			#a weekday weight (i.e. "no" in column 5 of the spreadsheet)
			if (backwards_data[data_position][2] in animals_copy) and ("no" in backwards_data[data_position][4]):
				try:
					animal_weight = int(backwards_data[data_position][3])
					
				except ValueError:
					pass #print "Couldn't get weight at %s, skipping to next cell" % data_position
				else:
					if countdown[backwards_data[data_position][2]] > 0:
						weekday_weights[backwards_data[data_position][2]].append(animal_weight)
						countdown[backwards_data[data_position][2]] -= 1
			data_position += 1

		print "Latest weekday weights: " + str(weekday_weights) + "\n"
		if not AllDaysRetrieved(countdown):
			raise Exception("Could not find weekly weight for all animals")

		#================================================================================================================

		#make a dict with animal ID keys (str) and True or False values if the animal weighed more than 90% of 
		#its max (weekend) weight or less, respectively. Days equal to 90% of its max make
		#the animal "false" in IsHeavyEnoughDict

		IsHeavyEnoughDict = {}
		for animal in self.animals_to_analyze:
			for each in weekday_weights[animal]:
				if float(each) > (0.9*(maxes[animal])):
					IsHeavyEnoughDict[animal] = True
				else:
					IsHeavyEnoughDict[animal] = False
					break
		return IsHeavyEnoughDict

	#====================================================================================================================
	#====================================================================================================================

	def format_data_for_graph(self):
		'''
		Returns a dict with animal IDs (str) as keys and a list of lists [[date objects list], [weights as ints list], 
			 [is_maxwgt list of Booleans]] as values.
		e.g. {"Q4":[[dates], [weights]]}
		'''
		def date_string_to_object(date_string):
			'''
			Takes in a date as a string from the spreadsheet (format 'month/day/year hrs:min:secs' or 'month/day/year')
			and returns that date as a date object from the datetime module
			'''
			#make splat, which is a list with date info e.g. ['month', 'day', 'year', 'hrs', 'min', 'sec']
			#makes date_obj, which is a python datetime object
			formatted = date_string.replace(":", "/").replace(" ", "/")
			splat = formatted.split("/")
			#splat[2] is year, splat[0] is month, and splat[1] is day. This is the format required by datetime.date
			date_obj = datetime.date(*(map(int, [splat[2], splat[0], splat[1]])))
			return date_obj
			
		data_copy = self.data[:]
		animals = self.animals_to_analyze[:]
		graph_dict = {}
		
		for animal in animals:
			print "Getting data for %s" % animal
			data_position = 0
			#dates is a list of date objects
			dates = []
			#weights is a list of weights corresponding to the date objects above
			weights = []
			#maxweight is a list of true or false for whether each date/weight pair was max weight "true"/"yes"
			#or a normal weekly weight "false"/"no" in data_copy[data_position][4]
			is_maxwgt = []
			while (data_position < self.data_list_length):

				if (data_copy[data_position][2] == animal):
					try:
						wgt = int(data_copy[data_position][3])
						weights.append(wgt)
					except ValueError:
						pass #print "Couldn't get weight at %s, skipping to next cell" % data_position
							 #used for testing

					else: 
						date = date_string_to_object(data_copy[data_position][0])
						dates.append(date)
						if "yes" in data_copy[data_position][4]:
							is_maxwgt.append(True)
						else:
							is_maxwgt.append(False)

				data_position += 1

			#after it has gotten dates, weights, is_maxwgt for each animal, put that info in graph_dict with 
			#animal ID as the key for your list of lists
			graph_dict[animal] = [dates, weights, is_maxwgt]
		return graph_dict

	#====================================================================================================================
	#====================================================================================================================
	#TODO test this method better, lots of confusing while loops here
	def regression(self):
		'''
		Returns 2 lists in a tuple: a weekend weights list, and a list of average weights from the most recent 4 weekdays (during
			water reprivation) associated with those weekend weights. 
		'''

		class addAppend(object):
			'''
			A class the counts to 4 items in a list then averages those items, helps in a while loop below
			'''

			def __init__(self):
				self.intList = []
				self.avg = False

			def addInt(self, num):
				if len(self.intList) < 4:
					self.intList.append(num)
				elif len(self.intList) == 4:
					summed = sum(self.intList)
					self.avg = summed/4.0
				else:
					pass

		weekend_weights = []
		weekday_avgs = []

		data_rev = self.data[::-1]
		animals_copy = self.animals_to_analyze[:]

		for animal in animals_copy:
			data_position = 0
			while (data_position < self.data_list_length):
				if (data_rev[data_position][2] == animal) and ("yes" in data_rev[data_position][4]):
					new_position = data_position
					count_four = addAppend()
					weekend_wgt = None
					while not count_four.avg and (new_position < self.data_list_length):
						if (data_rev[new_position][2] == animal) and ("no" in data_rev[new_position][4]):
							try:
								weekend_wgt = int(data_rev[data_position][3])
								weekday_wgt = int(data_rev[new_position][3])
							except ValueError:
								pass
							else:
								count_four.addInt(weekday_wgt)
						new_position += 1
					if type(count_four.avg) is float:
						weekday_avgs.append(count_four.avg)
						weekend_weights.append(weekend_wgt)
				data_position += 1

		return (weekend_weights, weekday_avgs)


	#====================================================================================================================
	#====================================================================================================================


	


