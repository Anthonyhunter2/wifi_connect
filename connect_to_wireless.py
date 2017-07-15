#!/usr/bin/python3

from re import search
import os
from subprocess import Popen
from time import sleep
from collections import OrderedDict
def check_for_wifi_card():
	dir_to_check = "/sys/class/net"
	list_dir = os.listdir(dir_to_check)
	for item in list_dir:
		if search('^w.*', item):
			return item
def write_info_to_tmpfile():
	wifi_card = check_for_wifi_card()
	with open("testfile.tmp","w") as writefile:
		scan_router = Popen(["iwlist", wifi_card , "scan"], stdout=writefile)
		writefile.close()
	sleep(1)
	gather_info_from_tmpfile()

def gather_info_from_tmpfile():
	possible = OrderedDict({})
	file_name = open("testfile.tmp","r")
	grouped_up = []
	count = 1
	for line in file_name.readlines():
		line = line.replace(":"," ")
		line = line.split(" ")
		line = list(filter(None, line))
		if "Address" in line or "ESSID" in line or "Frequency" in line:
			grouped_up.append(line)
	for item in grouped_up:	
		key = "Choice "+str(count)+":"
		if "Address" in item:
			address = ":".join(item[4:])
			address = address.split('\n')[0]
			possible.setdefault(key, []) 
			possible[key].append("Address, "+address)
		elif "Frequency" in item:
			freq = item[1]
			possible.setdefault(key, []) 
			possible[key].append("Frequency, "+freq)
		elif "ESSID" in item:
			essid = " ".join(item[1:])
			essid = essid.split('\n')[0]
			possible.setdefault(key, []) 
			possible[key].append("ESSID, "+essid)
			count = count +1 
	for choice in possible:
		print(choice, possible[choice])
	os.remove("testfile.tmp")

#gather_info_from_tmpfile()
write_info_to_tmpfile()
