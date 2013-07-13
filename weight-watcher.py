#!/usr/bin/python

import sys
import pylab
import argparse
from spreadsheet import Spreadsheet

class WeightWatcher(object):

	def __init__(self):
		'''
		self.data is an instance of the Spreadsheet class
		
		'''
		#TODO make spreadsheet url work here with command line options, as well as alternate sheet names
		#self.data is an instance of the Spreadsheet class in spreadsheet.py
		self.data = Spreadsheet(username, password)


		
