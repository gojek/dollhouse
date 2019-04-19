import ConfigParser
import sys
import os

#get single value of the section
def get_value(section,name):
	config = ConfigParser.ConfigParser()
	config.read('utils/config.property')
	return  config.get(section,name)

#get all the values of the section in dict format
def get_allvalues(section):
	config = ConfigParser.ConfigParser()
	config.read('utils/config.property')
	return dict(config.items(section))
