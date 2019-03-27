from jnpr.junos import Device
from lxml import etree
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

def verifyandconfigure(yamload,THIS_DIR,username,password):
	for key in yamload:
		dev = Device(key,user =username,passwd = password,port=22)
		dev.open()
		for task in yamload[key]:
			if task["name"] == "l2agg" or task["name"] == "l3agg":
				data = dev.rpc.get_config(filter_xml='chassis/aggregated-devices')
				if data.findtext(".//device-count") == None:
					print("chassis aggregated-devices ethernet device-count should be configured to add aggrgates")
					exit()
				elif task["aggnumber"] >= int(data.findtext(".//device-count")):
					print("Aggregated-devices ethernet device-count configured  is %s less than aggnumber in task %s at device %s" %(str(data.findtext(".//device-count")), task["name"] , yamload[key] ))
					exit()
				for interface in task["interfaces"]:
					xml="<configuration><interfaces><interface><name>"+interface+"</name></interface></interfaces></configuration>"
					data2 = dev.rpc.get_config(filter_xml=etree.XML(xml))
					if data2.findtext(".//interface") != None:
						print("interface %s in task %s at device %s has current configuration" %(interface,task["name"] , yamload[key]))
						exit()
			elif task["name"] == "l2agg" or task["name"] == "l3irb":
				data = dev.rpc.get_vlan_information()
				if QFX in dev.facts["RE0"]["model"]:
					for vlan in task["vlans"]:
						found = False
						for vl in data.findall(".//l2ng-l2ald-vlan-instance-group"):
							if str(vl.find(".//l2ng-l2rtb-vlan-name").text) == vlan["vlname"] and int(vl.find(".//l2ng-l2rtb-vlan-tag").text) == vlan["vlnumber"]:
								found = True
								break
						if found == False:
							for tas in yamload[key]:
								create = False
								if tas["name"] =="createvlan":
									for  v in tas["vlans"]:
										if v["vlname"] == vlan["vlname"] and v["vlnumber"] == vlan["vlnumber"]:
											create = True
											break
							if create == False:
								print("Vlan %s in task %s for device %s has to be created"%(vlan,task["name"],yamload[key]))
								exit()
			elif task["name"] == "aggaddintf":
				for interface in task["interfaces"]:
					xml="<configuration><interfaces><interface><name>"+interface+"</name></interface></interfaces></configuration>"
					data2 = dev.rpc.get_config(filter_xml=etree.XML(xml))
					if data2.findtext(".//interface") != None:
						print("interface %s in task %s at device %s has current configuration" %(interface,task["name"] , yamload[key]))
						exit()
				agg = "ae"+task["aggnumber"]
				xml="<configuration><interfaces><interface><name>"+agg+"</name></interface></interfaces></configuration>"
				data2 = dev.rpc.get_config(filter_xml=etree.XML(xml))
				if data2.findtext(".//interface") == None:
						print("Note : Aggregate interface %s in task %s at device %s is not configured" %(agg,task["name"] , yamload[key]))
			elif task["name"] == "aggdelintf":
				for interface in task["interfaces"]:
					xml="<configuration><interfaces><interface><name>"+interface+"</name></interface></interfaces></configuration>"
					data2 = dev.rpc.get_config(filter_xml=etree.XML(xml))
					if data2.findtext(".//bundle") != str("ae"+task["aggnum"]):
						print("Error: Interface %s is not configured under aggregate %s at task %s at device %s"%(interface,task["aggnum"],task["name"],yamload[key]))
						exit()
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
			conf = TEMPLATE_ENVIRONMENT.get_template("QFX").render(yamload[key])
			with Config(dev, mode='private') as cu:
				cu.load(conf, format='set')
				cu.pdiff()
				cu.commit()
			print("CONF loaded successfully in {}",key)
			dev.close()
		else:
			print("Unsupported Platform")	





def main():
	ymlfilename , username = parseoptions()
	password = getpass.getpass()
	THIS_DIR = str(os.path.dirname(os.path.abspath(__file__)))
	fob =open(ymlfilename).read()
	yamload = yaml.load(fob)
	verifyandconfigure(yamload,THIS_DIR,username,password)			

if __name__ == "__main__":
	main()
