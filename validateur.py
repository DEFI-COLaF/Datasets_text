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
	issue_bool = True
	"""for dir_racine in os.listdir("."):
		if not os.path.isfile(dir_racine):
			for dir_dataset in os.listdir(dir_racine):
				if not os.path.isfile(f'{dir_racine}/{dir_dataset}'):
					for xml_file in os.listdir(f'{dir_racine}/{dir_dataset}'):"""
	for xml_file in os.listdir("Eltec-fra/dataset_colaf/"):
		xml_doc = ET.parse(f'Eltec-fra/dataset_colaf/{xml_file}')	
		validate_bool= rng_schema.validate(xml_doc)
		if not validate_bool:
			print(f'problème dans le fichier {xml_file}')
			log = rng_schema.error_log
			print(log.last_error)
			issue_bool = False
	for domaines in os.listdir("OpenSubtitles/dataset_colaf/"):
		for annee in os.listdir("OpenSubtitles/dataset_colaf/"+domaines+"/"):
			for xml_file in os.listdir(f"OpenSubtitles/dataset_colaf/{domaines}/{annee}/"):
				xml_doc = ET.parse(f'OpenSubtitles/dataset_colaf/{domaines}/{annee}/{xml_file}')	
				validate_bool= rng_schema.validate(xml_doc)
				if not validate_bool:
					print(f'problème dans le fichier {xml_file}')
					log = rng_schema.error_log
					print(log.last_error)
					issue_bool = False
	if issue_bool:
		sys.exit(0)
	else:
		sys.exit(1)


if __name__ == "__main__":
	apply_rng()
