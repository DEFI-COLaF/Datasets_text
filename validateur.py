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
	for root, dir, files in os.walk("."):
		if 'dataset_colaf' in root:
			for file in files:
				if 'xml' in file:
					xml_doc = ET.parse(f'{root}/{file}')
					validate_bool = rng_schema.validate(xml_doc)
					if not validate_bool:
						print(f'problème dans le fichier {xml_doc}')
						log = rng_schema.error_log
						print(log.last_error)
						issue_bool = False

	if issue_bool:
		sys.exit(0)
	else:
		sys.exit(1)


if __name__ == "__main__":
	apply_rng()
