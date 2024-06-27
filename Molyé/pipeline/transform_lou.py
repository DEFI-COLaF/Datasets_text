import os

import PyPDF2

import molyé_util as m_util
import annotation




def simple_convert(title):
    g_books = "source/Google_books"
    pdfs = f"{g_books}/pdf"
    txts = f"{g_books}/txt"
    pdf_file = f"{pdfs}/{title}.pdf"
    txt_file = f"{txts}/{title}.txt"
    pdfReader = PyPDF2.PdfReader(open(pdf_file, mode="rb"), "rb")
    text = m_util.read_pdf_object(pdfReader)
    with open(txt_file, mode="w") as f:
        f.write(text)
    return text




def convert_pdfs(g_books = "source/Google_books"):
    pdfs = f"{g_books}/pdf"
    txts = f"{g_books}/txt"
    files = os.listdir(pdfs)
    texts = [simple_convert(f[:-4]) for f in files]

def disjunctive_tag(in_file, out_file, disjunctive, lang):
    file_text = m_util.read_file(in_file)
    interesting_lines = m_util.check_lines_direct(file_text, disjunctive)
    out_text = annotation.tag_langs_prose(file_text, interesting_lines, lang)
    with open(out_file, mode="w") as f:
        f.write(out_text)
    return out_text




def main():
    lou_regular = ["mo", "moin", "to", "li", "yé", "vou", "nou",
                   "cé", "pa", "pou", "nou", "maite", "nég",
                   "sré", "té", "apé", "ap", "laïé", "couri",
                   "mossié", "pli", "di", "mouri"]

    lou_special = ["moué", "toué" "y lé", "y l’est", "y l’été", "y pas",
                   "sti", "c't", "qué", "l'y", "mon la", "son la", "ti"]
    lou_regular += lou_special
    # test lang tagging
    wiki_raw = "../source/wikisource"
    wiki_tei = "../dataset_colaf/wikisource"


    ybars = "L_Habitation_Saint_Ybars.xml"
    une_deux = "Une_de_perdue_deux_de_trouvées_TOME_I.xml"
    une_deux_two= f"Une_de_perdue_deux_de_trouvées_TOME_II.xml"

    lou_works = [ybars, une_deux, une_deux_two]
    for f in lou_works:
        disjunctive_tag(f"{wiki_tei}/{f}", f"{wiki_tei}/{f}", lou_regular, "lou")


if __name__ == '__main__':
    main()




