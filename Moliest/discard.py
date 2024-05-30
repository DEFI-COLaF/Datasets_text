# def read_pdf_object(pdfReader):
#     all_text = ""
#     for page in pdfReader.pages:
#         all_text = all_text + page.extract_text()
#     return all_text
#
# def extract_web_pdf(url):
#     doc_obj = requests.get(url, headers = {'User-Agent': 'Me 2.0'})
#     doc_bytes = doc_obj.content
#     pdfReader = PyPDF2.PdfReader(io.BytesIO(doc_bytes), "rb")
#     all_text = read_pdf_object(pdfReader)
#     return all_text



# with open(f"{raw_wiki_folder}/{wiki_title}.html", mode="w") as f:
#     f.write(wiki_soup.body.prettify())

# import PyPDF2
#
# #probably will change to fuzzy matching
# def get_rid_of_title(page_text, book_title):
#     page_lines = page_text.split("\n")
#     first_line = page_lines[0]
#     first_line = re.sub(book_title.upper(), "", first_line)
#     first_line = re.sub(r"\d+", "", first_line)
#     page_lines[0] = first_line
#     page_text = "\n".join(page_lines)
#     return page_text
# def fix_common_pdf_errors(page_text, book_title):
#     page_text = re.sub("<<", "«", page_text)
#     page_text = re.sub(">>", "»", page_text)
#     page_text = re.sub(r" \.", r".", page_text)
#     page_text = get_rid_of_title(page_text, book_title)
#     return page_text
#
# def identify_small_roman(line):
#     romans = re.findall(r"C?L?I?X{0,3}V?I{0,3}\.?", line)
#     return [r for r in romans if len(r)]
#
# def identify_section_header(page_text):
#     pass
#
# pdf_file = open("Google_books/pdf/L_autre_monde.pdf", "rb")
# pdf_reader = PyPDF2.PdfReader(pdf_file)
# print(len(pdf_reader.pages))
# test_page = pdf_reader.pages[23].extract_text()
# print(fix_common_pdf_errors(test_page, "L'autre monde"))