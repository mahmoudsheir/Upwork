from jnpr.junos import Device
import yaml
import os
import argaprse
from jinja2 import Environment, FileSystemLoader
import getpass

def parseoptions():
	desc = """
	Please Provide the below Mandatories for the script:
	YML File for the operation Requested include the path to the file if it is not on the same folder
	Username
	Password
	For the model of YML file please refer to YML example
	""" 
	parser = argparse.ArgumentParser(description = desc , usage = '%(prog)s YML Username Vendor RouterIP')
	parser.add_argument("YML" ,help = "Operations YML file")
	parser.add_argument("Username", help ="Routers Username")
	args = vars(parser.parse_args())
	return args.values()

def main():
	ymlfilename , username = parseoptions()
	password = getpass.getpass()
	THIS_DIR = str(os.path.dirname(os.path.abspath(__file__)))
	fob =open(ymlfilename).read()
	yamload = yaml.load(fob)
	for key in yamload:
		dev = Device(key,user =username,passwd = password,port=22)
		dev.open()
		if MX in dev.facts["RE0"]["model"]:
			TEMPLATE_ENVIRONMENT = Environment(autoescape=False,loader=FileSystemLoader(THIS_DIR),trim_blocks=False)
			conf = TEMPLATE_ENVIRONMENT.get_template("MX").render(yamload[key])
			with Config(dev, mode='private') as cu:
				cu.load(conf, format='set')
				cu.pdiff()
				cu.commit()
			print("CONF loaded successfully in {}",key)
			dev.close()
		elif QFX in dev.facts["RE0"]["model"]:
			TEMPLATE_ENVIRONMENT = Environment(autoescape=False,loader=FileSystemLoader(THIS_DIR),trim_blocks=False)
			conf = TEMPLATE_ENVIRONMENT.get_template("MX").render(yamload[key])
			with Config(dev, mode='private') as cu:
				cu.load(conf, format='set')
				cu.pdiff()
				cu.commit()
			print("CONF loaded successfully in {}",key)
			dev.close()
		else:
			print("Unsupported Platform")			

if __name__ == "__main__":
	main()
