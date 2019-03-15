import paramiko
from jinja2 import Environment, FileSystemLoader
from jnpr.junos.utils.config import Config
import yaml
import argparse
from jnpr.junos import Device
import getpass
import os
import time

def parseoptions():
	desc = """
	Please Provide the below Mandatories for the script:
	YML File for the operation Requested include the path to the file if it is not on the same folder
	Username
	Password
	Vendor
	RouterIP
	For the model of YML file please refer to YML example
	""" 
	parser = argparse.ArgumentParser(description = desc , usage = '%(prog)s YML Username Vendor RouterIP')
	parser.add_argument("YML" ,help = "Operations YML file")
	parser.add_argument("Username", help ="Routers Username")
	parser.add_argument("Vendor", choices=['Cisco', 'Juniper'], help = "Select Either Cisco or Juniper Router")
	parser.add_argument("RouterIP", help ="Router IP")
	args = vars(parser.parse_args())
	return args.values()

def main():
	ymlfilename , username, vendor, routerip = parseoptions()
	password = getpass.getpass()
	THIS_DIR = str(os.path.dirname(os.path.abspath(__file__)))
	fob =open(ymlfilename).read()
	yamload = yaml.load(fob)
	if  vendor == "Juniper":
		TEMPLATE_ENVIRONMENT = Environment(autoescape=False,loader=FileSystemLoader(THIS_DIR),trim_blocks=False)
		conf = TEMPLATE_ENVIRONMENT.get_template("jnpr").render(yamload)
		dev = Device(host=routerip ,user=username ,passwd=password, port=22)
		dev.open()
		with Config(dev, mode='private') as cu:
			cu.load(conf, format='set')
			cu.pdiff()
			cu.commit()
		dev.close()
		print(" Configuration done successfully")
	elif vendor == "Cisco":
		TEMPLATE_ENVIRONMENT = Environment(autoescape=False,loader=FileSystemLoader(THIS_DIR),trim_blocks=False)
		conf = TEMPLATE_ENVIRONMENT.get_template("csco").render(yamload)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(routerip,22,username,password)
		channel = ssh.invoke_shell()
		for line in  conf.split("\n"):
			buff =""
			channel.send(line)
			channel.send("\n\n")
			while True:
				if channel.recv_ready():
					resp = str(channel.recv(9999))
					buff += resp
					continue
				else:
					break
			print(line)
			time.sleep(1)
		ssh.close()
		print(" Configuration done successfully")




if __name__ == "__main__":
	main()
