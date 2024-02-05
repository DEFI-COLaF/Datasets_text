import lxml.etree as ET
import click
import sys
import os 

@click.command()
@click.argument("rng_file")
def apply_rng(rng_file):
	"""Applique le rng sur le XML qui vient d'être ajouté"""
	rng_doc = ET.parse(rng_file)
	rng_schema = ET.RelaxNG(rng_doc)
	for dir_racine in os.listdir("."):
		if not os.path.isfile(dir_racine):
			for dir_dataset in os.listdir(dir_racine):
				if not os.path.isfile(f'{dir_racine}/{dir_dataset}'):
					for xml_file in os.listdir(f'{dir_racine}/{dir_dataset}'):	
						xml_doc = ET.parse(f'{dir_racine}/{dir_dataset}/{xml_file}')	
						validate_bool= rng_schema.validate(xml_doc)
						if validate_bool:
							sys.exit(0)
						else:
							sys.exit(1)
        
        
if __name__=="__main__":
	apply_rng()
