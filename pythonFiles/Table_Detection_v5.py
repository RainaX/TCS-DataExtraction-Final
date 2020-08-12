
"""
Author: Xiaoye, Yudi
Date created: 7/13/2020
Date last modified: 7/13/2020
Python Version: 3.8
Description: this script is used to find the financial statements in a 
10-K pdf and split each into a single pdf
"""


# Please install below packages before you run the script
# %pip install PyPDF2
# %pip install pdftotext
# %pip install pdfplumber

# import packages
from PyPDF2 import PdfFileReader, PdfFileWriter
import pdfplumber
import pdftotext
import re
import os
import glob

# Dictionary stores the page details for each PDF
pdf_dict = {}

# The path where you store all the input 10-K PDFs
PDF_FILES_PATH = '/home/ubuntu/webserver/uploadedFiles/'

# The path where you store all the splitted PDFs
RESULT_FILES_PATH = '/home/ubuntu/webserver/outputSinglePages/'

# Key words list for item 8, item 9 and item 15
key_words = ["item 8", "item 9", "financial statement schedule"]

# Regular expression for headers, continued_headers, table_endings and search_endings
headers = r"^(consolidate)d?.*(statement)s?.*$|^(consolidate)d?.*(balance).*(sheet)s?.*$"
continued_headers = r"(continue)d?"
table_endings = r"^.*(see).*(notes).*$|^.*(notes).*(statement)s?.*$"
search_endings = r"^(note)s? to (consolidate)d? financial (statement)s?$"

def pdf_to_text(file_name):
    '''
    Read a pdf and transfer it to text string using pdftotext
    :param file_name: file name of a pdf
    '''
    
    path = PDF_FILES_PATH + file_name + ".pdf" # path for input pdf
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)
    return pdf

def extract_page_num_from_single_line(line):
    '''
    Extract page number from a line in the content page.
    :param line: a line of a content page; string
    '''

    line_content = line.split(" ")
    if len(line_content) > 0:
        if line_content[-1].isnumeric():    # Get pageNumber in that line
            return eval(line_content[-1])
        if re.match(r"[0-9]+-[0-9]+", line_content[-1]) is not None:    # If contains no numeric text
            return eval(line_content[-1].split("-")[0])
    return -1

def extract_page_num_from_single_page(page_text):
    '''
    Extract written page number from a page.
    :param current_page: a string format of a page
    '''

    if page_text is None:
        return -2
    else:
        page_text = page_text.strip()
        lines = re.split(r'\n+', page_text)
        last_line = lines[-1]
        if "www.sec.gov" in last_line:
            last_line = lines[-2]
        if last_line.strip().isnumeric():
            return eval(last_line)
        else:
            return -1

def find_actual_page_number(pdf, written_page_num):
    '''
    Calculate actual page number of one page in the pdf according to its 
    written page number.
    : param pdf: PDF object read by pdftotext
    : param written_page_num: written page number 
    '''

    times = 0
    index = written_page_num - 1
    prev_empty = False
    while 0 < index < len(pdf) and times < len(pdf):
        times += 1
        current_page = pdf[index]
        current_page_num = extract_page_num_from_single_page(current_page)
        if current_page_num == eval(str(written_page_num)):
            if prev_empty:
                return index
            return index + 1
        else:
            if current_page_num == -1:
                prev_empty = True
                index += 1
            else:
                if prev_empty:
                    prev_empty = False
                if current_page_num == -2:
                    index += 1
                else:
                    index += (eval(str(written_page_num)) - current_page_num)
    return -1

def split_pdf(infn, outfn, start_page, end_page):
    '''
    Split a pdf into sub-pdf using PyPDF2 according 
    to the start and end page.
    : param infn: input pdf
    : param outfn: output pdf
    : param start_page: start page for splitting
    : param end_page: end page for splitting
    '''

    pdf_output = PdfFileWriter()
    pdf_input = PdfFileReader(open(infn, 'rb'))
    page_count = pdf_input.getNumPages()
    for i in range(start_page, end_page+1):
        pdf_output.addPage(pdf_input.getPage(i))
    pdf_output.write(open(outfn, 'wb'))

def locate_table_pages(pdf, file_name):
    '''
    Locate the start and end page numbers of financial 
    statement section. Normally, it will be item 8. Sometimes,
    it may also be item 15.
    : param pdf: PDF object read by pdftotext
    : param file_name: file name of a pdf
    '''
    
    this_dict = {}  # Store the start and end page for the current pdf
    content_page_exist = False  # Flag: whether the pdf has content page

    for i in range(len(pdf)):
        page_text = pdf[i].lower()
        if page_text is None:
            continue
        
        # If find 'item 8' and 'item 9' exist in the same page, 
        # then content page exists
        if key_words[0] in page_text and key_words[1] in page_text:
            content_page_exist = True
            
            lines_in_page = page_text.splitlines()
            index_of_line = 0   # Record the index for current line

            # Process each line of content page to find the start
            # and end page of financial statement section 
            for line in lines_in_page:

                # Find line of item 8 and get its actual page number
                if key_words[0] in line:
                    item8_written_page_num = extract_page_num_from_single_line(line)

                    # If no page number found in the line, then go to next line
                    # to find page number (solved double line problem)
                    if item8_written_page_num == -1:
                        item8_written_page_num = extract_page_num_from_single_line(lines_in_page[index_of_line + 1])
                        start = index_of_line + 2   # Record the start line for item 9
                    else:
                        start = index_of_line + 1
                    actual_item8_page_number = find_actual_page_number(pdf, item8_written_page_num)
                    
                    # Find line of item 9 and get its actual page number
                    for i in range(start, len(lines_in_page) - 1):
                        if key_words[1] in lines_in_page[i]:
                            item9_written_page_num = extract_page_num_from_single_line(lines_in_page[i])
                            if item9_written_page_num == -1:
                                item9_written_page_num = extract_page_num_from_single_line(lines_in_page[i + 1])
                            actual_item9_page_number = find_actual_page_number(pdf, item9_written_page_num)
                            break
                    break
                index_of_line += 1
                
            # If financial statement section is in item 15. Then use
            # the page number of item 15 as 'start' and the end of the pdf as 'end'
            if actual_item9_page_number - actual_item8_page_number <= 1:
                index_of_line = 0
                for line in lines_in_page:
                    if key_words[2] in line:
                        item15_written_page_num = extract_page_num_from_single_line(line)
                        if item15_written_page_num == -1:
                            item15_written_page_num = extract_page_num_from_single_line(lines_in_page[index_of_line + 1])
                        actual_item15_page_number = find_actual_page_number(pdf, item15_written_page_num)

                        # Record the start and end page in this_dict
                        this_dict["start"] = actual_item15_page_number
                        this_dict["end"] = len(pdf) + 1
                        break
                    index_of_line += 1
            else:
                # Else, use the page number fo item 8 and item 9 as 'start' and 'end'
                this_dict["start"] = actual_item8_page_number
                if actual_item9_page_number - actual_item8_page_number >= 30:
                    this_dict["end"] = actual_item8_page_number + 30
                else:
                    this_dict["end"] = actual_item9_page_number
            break

        # If the first 10 pages of the pdf has no content page, then break
        if i > 10:
            break
   
    # If there is no content page, then scan the whole pdf
    if content_page_exist == False:
        this_dict["start"] = 1
        this_dict["end"] = len(pdf) + 1
    
    # Update to pdf_dict
    global pdf_dict
    pdf_dict[file_name] = this_dict

def get_statements_page_num(pdf, file_name):
    '''
    Extract the page number(s) for each financial statement
    in the 10-K report
    : param pdf: PDF object read by pdftotext
    : param file_name: file name of a pdf
    '''

    # Read the 'start' and 'end' info for current pdf from pdf_dict
    current_pdf_dict = pdf_dict[file_name]
    start = current_pdf_dict['start']
    end = current_pdf_dict['end']

    # Extract text for each page and check if it is table page
    pages_dict = {}
    for i in range(start-1, end-1):
        page = pdf[i]
        lines_in_page = page.splitlines()

        # If found "notes to consolidated financial statements",
        # then stops ahead of time. This sentence marks the end of
        # actual financial statement pages section
        ifBreak = False
        for line in lines_in_page[0:10]:
            match = re.match(search_endings, line.lower().strip())
            if match != None:
                ifBreak = True
                break
        if ifBreak == True:
            break
        
        # Search the first 10 lines of one page to check if it 
        # contains continued_headers or headers
        for line in lines_in_page[0:10]:
            match0 = re.search(continued_headers, line.lower().strip())
            match1 = re.search(headers, line.lower().strip())

            # Record it as start page of one table only if it contains headers
            # while not continued_headers
            if match0 == None:
                if match1 != None:
                    table_start_page = i
                    table_end_page = -1

                    # Check whether the end of the current page contains table_endings.
                    # If so, record the current page as end page of the table
                    lines_in_page_strip = page.strip().splitlines()
                    for line in lines_in_page_strip:
                        match2 = re.search(table_endings, line.lower())
                        if match2 != None:
                            table_end_page = i
                            break

                    # If not, record next page as end page of the table
                    if table_end_page == -1 :
                        table_end_page = table_start_page
                        match3 = None
                        while match3 == None and table_end_page - table_start_page <1 and table_end_page < len(pdf)-1:  # maximum 2 pages
                            table_end_page += 1
                            for line in pdf[table_end_page].strip().splitlines():
                                match3 = re.search(table_endings, line.lower())
                                if match3 != None:
                                    break

                    # Update to pages_dic
                    if table_end_page != -1:
                        if table_start_page in pages_dict.values():
                            # Remove duplicate pages within between
                            pages_dict = {key:val for key, val in pages_dict.items() if val != table_start_page}
                        pages_dict[table_start_page] = table_end_page
                    break
    print(pages_dict)

    # Update to pdf_dict
    pdf_dict[file_name]['detail_pages'] = pages_dict

    # Split pages based on pages_dict
    path = PDF_FILES_PATH + file_name + ".pdf" # path for input pdf
    if pages_dict:
        for k in pages_dict.keys():
            split_pdf(path, RESULT_FILES_PATH + "{}_{}_{}_split.pdf".format(file_name, k, pages_dict[k]), k, pages_dict[k])
    else:
        print("****No related contents found for {}. Please check for it!****".format(file_name))

def delete_text_pdf():
    '''
    Use pdfplumber to delete no-table pure text pdfs
    that was wrongly detected in the previous step
    '''
    
    os.chdir(RESULT_FILES_PATH)
    extension = 'pdf'
    all_filenames = [i for i in glob.glob("*.{}".format(extension))]
    for filename in all_filenames:

        # Delete pure text pages
        pdf = pdfplumber.open(filename)
        isText = False
        page = pdf.pages[0]
        table_settings = {"vertical_strategy": "text"} # add table setting for pdfplumber
        table = page.extract_table(table_settings)
        if table == None:
            isText = True
            print("{} has no tables. Delete!".format(filename))
            os.remove(filename)
            continue

        # Further delete sub-content page not deleted in the previous step.
        # We will use the criteria if this page contains 'index' keyword or there are
        # more than 3 statement headers in this page to decide if it's sub-content pgae
        with open(filename, "rb") as f:
            pdf2 = pdftotext.PDF(f) 
        isSubContent = False
        header_count = 0
        lines_in_page = pdf2[0].splitlines()

        for line in lines_in_page:
            match1 = re.search("index", line.lower().strip())
            match2 = re.search(headers, line.lower().strip())

            # If find "index" keyword then break
            if match1 != None:
                isSubContent = True
                break

            # If find header in this line, then add to header_count
            if match2 != None:
                header_count += 1

            # If hearder count is great than 3, then break
            if header_count >= 3:
                isSubContent = True
                break
        if isSubContent == True:
            print("{} has no tables. Delete!".format(filename))
            os.remove(filename)
    os.chdir("..")

if __name__ == '__main__':
    path = PDF_FILES_PATH
    files = os.listdir(path)
    for i in range(len(files)):
        try:
            file_name = files[i].__str__().split(".")[0]
            if file_name != '':
                print("----Start to download for file {} {}".format(i, file_name))
                pdf = pdf_to_text(file_name)
                locate_table_pages(pdf, file_name)
                get_statements_page_num(pdf, file_name)
        except Exception as e:
            print("****Error in file {} {}****".format(i, file_name))
            continue
        print(" ")
    print("Finished all splits")
    print(" ")
    print("---Delete pure text files---")
    delete_text_pdf()
    print("Finished all!")
