import moliyé_util as m_util




#test lang tagging
ybars_file = "wikisource_TEI/L_Habitation_Saint_Ybars.xml"
une_deux_file = "wikisource_TEI/Une_de_perdue_deux_de_trouvées_TOME_I.xml"
une_deux_two_file = "wikisource_TEI/Une_de_perdue_deux_de_trouvées_TOME_II.xml"



ybars = m_util.read_file(ybars_file)
une_deux = m_util.read_file(une_deux_file)
une_deux_two = m_util.read_file(une_deux_two_file)


disjunctive = ["mo", "moin", "to", "li", "yé", "vou", "nou",
                   "cé", "pa", "pou", "nou", "maite", "nég",
                   "sré", "té", "apé", "ap", "laïé"]


lou_expanded = [ m_util.expand_disjunctive(n) for n in disjunctive]

lou_special = ["moué", "y lé", "l'été", "sti", "c’t", "qué", "l'y", "mon la", "son la", "couri"]
special_expanded = [ m_util.expand_disjunctive(n) for n in lou_special]
interesting_lines = m_util.check_lines_direct(une_deux, lou_special)
interesting_two = m_util.check_lines_direct(une_deux_two, lou_special)
print(len(interesting_lines))
print(len(interesting_two))

colaf_ybars_file = "dataset_colaf/L_Habitation_Saint_Ybars.xml"
colaf_ybars = m_util.read_file(colaf_ybars_file)

lines = m_util.get_lines_of_interest(colaf_ybars, "lou", level="s")

ybars_interesting = m_util.check_lines_direct(ybars, disjunctive)
ybars_out = m_util.tag_langs_prose(ybars, ybars_interesting, "lou")
with open("dataset_colaf/L_Habitation_Saint_Ybars.xml", mode="w") as f:
    f.write(ybars_out)



ybars_tagged_file = "dataset_colaf/L_Habitation_Saint_Ybars.xml"



ybars_interesting = "\n".join([l for l in ybars_interesting])
print(ybars_interesting)
#print(len(interesting_lines.split()))


url = "https://archive.org/stream/b24865424/b24865424_djvu.txt"