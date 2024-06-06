




#test lang tagging
ybars_file = "wikisource_TEI/L_Habitation_Saint_Ybars.xml"
une_deux_file = "wikisource_TEI/Une_de_perdue_deux_de_trouvées_TOME_I.xml"
une_deux_two_file = "wikisource_TEI/Une_de_perdue_deux_de_trouvées_TOME_II.xml"



ybars = read_file(ybars_file)
une_deux = read_file(une_deux_file)
une_deux_two = read_file(une_deux_two_file)


disjunctive = ["mo", "moin", "to", "li", "yé", "vou", "nou",
                   "cé", "pa", "pou", "nou", "maite", "nég",
                   "sré", "té", "apé", "ap"]


lou_expanded = [ expand_disjunctive(n) for n in disjunctive]

lou_special = ["moué", "y lé", "l'été", "sti", "c’t", "qué", "l'y", "mon la", "son la", "couri"]
special_expanded = [ expand_disjunctive(n) for n in lou_special]
interesting_lines = check_lines_direct(une_deux, lou_special)
interesting_two = check_lines_direct(une_deux_two, lou_special)
print(len(interesting_lines))
print(len(interesting_two))

colaf_ybars_file = "dataset_colaf/L_Habitation_Saint_Ybars.xml"
colaf_ybars = read_file(colaf_ybars_file)

lines = get_lines_of_interest(colaf_ybars, "lou", level="s")

ybars_interesting = check_lines_direct(ybars, lou_disjunctive)
ybars_out = tag_langs_prose(ybars, ybars_interesting, "lou")
with open("dataset_colaf/L_Habitation_Saint_Ybars.xml", mode="w") as f:
    f.write(ybars_out)



ybars_tagged_file = "dataset_colaf/L_Habitation_Saint_Ybars.xml"



ybars_interesting = "\n".join([l for l in ybars_interesting])
print(ybars_interesting)
#print(len(interesting_lines.split()))


url = "https://archive.org/stream/b24865424/b24865424_djvu.txt"