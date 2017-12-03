#!/usr/bin/python3

from re import search
import os
import subprocess
from collections import OrderedDict
from sys import exit
import getpass
class Network():
	def __init__(self, name):
		self.name = name
		self.card = self.check_for_wifi_card()
	def check_for_wifi_card(self):
		dir_to_check = "/sys/class/net"
		list_dir = os.listdir(dir_to_check)
		for item in list_dir:
			if search('^w.*', item):
				return(item)
	def connect_known(self):
		ifup = subprocess.Popen(["nmcli", "c", "up", "id", self.name])
		ifup.communicate()
	def connect_nopass(self):
		first = subprocess.Popen(["nmcli", "con", "add", "con-name", self.name, "ifname", self.card, "type", "wifi", "ssid", self.name])
		first.communicate()
		second = subprocess.Popen(["nmcli", "c", "up", "id", self.name])
		second.communicate()
	def connect_unknown(self):
		first = subprocess.Popen(["nmcli", "con", "add", "con-name", self.name, "ifname", self.card, "type", "wifi", "ssid", self.name])
		first.communicate()
		self.password()
		self.connect_known()
	def disconnect(self):
		discon = subprocess.Popen(["nmcli", "c", "down", "id", self.name])
		discon.communicate()
	def password(self):
		password = getpass.getpass("Please Enter the Password for {}: ".format(self.name))
		first = subprocess.Popen(["nmcli", "con", "modify", self.name, "wifi-sec.key-mgmt", "wpa-psk"])	
		first.communicate()
		second = subprocess.Popen(["nmcli", "con", "modify", self.name, "wifi-sec.psk", password])
		second.communicate()
	
def output_of_wifi_scan():
	scan_router = subprocess.Popen(["nmcli", "dev", "wifi", "list" ], stdout=subprocess.PIPE)
	already_in_dict = []
	possible = OrderedDict({})
	count = 1
	for line in scan_router.stdout.readlines():
		line = line.decode("utf-8").strip("*").split()
		if "SSID" not in line:
			key = "Choice "+str(count)+":"
			full_name = " ".join(line[0:line.index("Infra")])
			if line[-1:] == "--":
				security = "\033[32mNo Password\033[0m"
			else:
				security = "\033[31mPassword Required\033[0m"
			value = "{}: {}".format(full_name, security)
			if full_name not in already_in_dict:
				already_in_dict.append(full_name)	
				possible[key] = value
				count += 1
	return(possible)
def are_you_connected():
	scan_router = subprocess.Popen(["nmcli", "dev", "wifi", "list" ], stdout=subprocess.PIPE)
	for line in scan_router.stdout.readlines():
		line = line.decode("utf-8").split()
		if "SSID" not in line:
			if line[0] == "*":
				full_name = " ".join(line[1:line.index("Infra")])
				return(full_name)

def maybe_connected():
	affirm = ["yes", "Yes", "y", "Y"]
	negitive = ["No", "no", "N", "n"]
	connected = are_you_connected()
	if connected:
		print("You are connected to \"{}\"".format(connected))
		disconnect = input("Would you like to disconnect from \"{}\"  y|n\n".format(connected))
		if disconnect in affirm:
			wifi = Network(connected)
			wifi.disconnect()
			exit()
		elif disconnect in negitive:
			pass
		else:
			print("Sorry please use \"y\" or \"n\"")
			maybe_connected()
def more_options_fun():
	affirm = ["yes", "Yes", "y", "Y"]
	negitive = ["No", "no", "N", "n"]
	save = []
	possible_connections = output_of_wifi_scan()
	for choices in possible_connections.items():
		print(" ".join(choices))
	more_options = input("\033[1mWould you like to connect to one of the networks above? y|n \033[0m\n")
	if more_options in affirm:
		answ = input("Which one? Just the number of your choice ie 2\n")
		for key, value in possible_connections.items():
			if answ in key:
				save.append(value.split(":")[0])
	elif more_options in negitive:
		print("Well then why are you here? Good Day Sir!.... \033[1;31mI said GOOD DAY\033[0m")
		exit()
	elif int(more_options) in range(len(possible_connections)):
		for key, value in possible_connections.items():
			if more_options in key:
				save.append(value.split(":")[0])
	else:
		print("Sorry I didn't see that option please try again")
		more_options_fun()
	if save:
		net = " ".join(save)
		if see_if_connected_before(net):
			conn = Network(net)
			conn.connect_known()
		elif not see_if_connected_before(net):
			for key, value in possible_connections.items():
				if net in value:
					if "No Password" in value:
						conn = Network(net)
						conn.connect_nopass()
					elif "Required" in value:
						conn = Network(net)
						conn.connect_unknown()
def see_if_connected_before(past_con):
	check_dir = "/etc/NetworkManager/system-connections"
	in_here = os.listdir(check_dir)
	if past_con in in_here:
		return(past_con)
def main():
	maybe_connected()
	more_options_fun()
main()
