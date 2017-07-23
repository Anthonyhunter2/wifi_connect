#!/usr/bin/python3

from re import search
import os
import subprocess
from time import sleep
from collections import OrderedDict
import binascii
from sys import exit
def check_for_wifi_card():
	dir_to_check = "/sys/class/net"
	list_dir = os.listdir(dir_to_check)
	for item in list_dir:
		if search('^w.*', item):
			return item
def output_of_wifi_scan():
	scan_router = subprocess.Popen(["nmcli", "dev", "wifi", "list" ], stdout=subprocess.PIPE)
	grouped_up = []
	possible = OrderedDict({})
	count = 1
	for line in scan_router.stdout.readlines():
		if b'Infra' in line:
			grouped_up.append(line.decode("utf-8").strip("*").strip("\n").strip(" "))
	for line in grouped_up:
		key = "Choice "+str(count)+":"
		line = line.split()
		full_name = " ".join(line[0:line.index("Infra")])
		security = line[-1]
		possible.setdefault(key, []) 
		possible[key].append(full_name)
		possible[key].append(security)
		count += 1
	for key in possible:
		if possible[key][1] == "--":
			print(key, possible[key][0], "No Password")
		else:
			print(key, possible[key][0], possible[key][1])
	return possible
def action_on_answer(dictonary, network_card):
	all_choices = []
	connect = input("Which Wifi Network would you like to connect to ? (Just Enter The Number): ")
	for answer in dictonary:
		all_choices.append(answer)
		choice_string = "Choice {}:".format(connect)
	if choice_string in all_choices:
		is_it_here = []
		network_id = dictonary[choice_string][0]
		checking_for_previous_connaction = os.listdir("/etc/NetworkManager/system-connections")
		for item in checking_for_previous_connaction:
			is_it_here.append(item)
		if network_id in is_it_here:	
				response = input("Would you like to be connected to {} ? y|n ".format(network_id))
				if response == "y"or response == "Y" or response == "yes":
					connect = subprocess.Popen(["nmcli", "c", "up", "id", network_id], stdout=subprocess.PIPE)
					for line in connect.stdout.readlines():
						print(line.decode("utf-8"))
				elif response == "n" or response == "N" or response == "no":
					connect = subprocess.Popen(["nmcli", "c", "down", "id", network_id], stdout=subprocess.PIPE)
					for line in connect.stdout.readlines():
						print(line.decode("utf-8"))
				else:
					print("Sorry I did not understand please use, y or n")	
		else:
			if "No Password" not in dictonary[choice_string]:
				print("This Seems to be a new connection")
				command = subprocess.Popen(["nmcli", "con", "add", "con-name", network_id, "ifname", network_card, "type", "wifi", "ssid", network_id], stdout=subprocess.PIPE)
				for line in command.stdout.readlines():
					print(line.decode("utf-8"))
				add_password = subprocess.Popen(["nmcli", "con", "modify", network_id, "wifi-sec.key-mgmt", "wpa-psk"], stdout=subprocess.PIPE)
				for line in add_password.stdout.readlines():
					print(line.decode("utf-8"))
				password = input("Please Enter the Password for {}: ".format(network_id))
				give_password = subprocess.Popen(["nmcli", "con", "modify", network_id, "wifi-sec.psk", password], stdout=subprocess.PIPE)
				for line in give_password.stdout.readlines():
					print(line.decode("utf-8"))
				connect = subprocess.Popen(["nmcli", "c", "up", "id", network_id], stdout=subprocess.PIPE)
				for line in connect.stdout.readlines():
					print(line.decode("utf-8"))
	else:
		print("Sorry I don't see that as a possible Choice")



action_on_answer(output_of_wifi_scan(), check_for_wifi_card())
