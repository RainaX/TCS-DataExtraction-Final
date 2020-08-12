# This is a testing code for demo.
# This code will read all pdf documents from input file,
# split those documents(just remain the first page), and
# output will be split documents
#
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def split_pdf(infn, outfn):
    pdf_output = PdfFileWriter()
    pdf_input = PdfFileReader(open(infn, 'rb'))
    page_count = pdf_input.getNumPages()
    pdf_output.addPage(pdf_input.getPage(0))
    pdf_output.write(open(outfn, 'wb'))


if __name__ == '__main__':
    path = "C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\out\\artifacts\\FileUpload_war_exploded\\uploadedFiles"  # dir of input file, also make sure there is an output file called output
    files = os.listdir(path)
    for file in files:
        infn = file.__str__()
        print(infn)
        outfn = "C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\output\\" + infn
        infn = path + "/" +infn

        print(outfn)
        split_pdf(infn, outfn)
