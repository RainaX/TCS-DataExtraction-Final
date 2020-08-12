# This is the version_1 code for locating and splitting pages of tables.
# Basic flow:
# 1. read pdf files from InputFiles
# 2. locate page number of "item 8"
# (use written page number to search for actual page number)
# 3. locate page number of tables
# (sub content format differs among different pdf)
# 4. split pages
#
# Problems:
# special cases unsolved

import os
import re
import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter

# index = page_num - 1
page_dict = {}
wrong_pdf = []
key_word = "item 8"
header_set = {"consolidated income statements", "consolidated statements of operations",
              "consolidated statements of comprehensive income", "consolidated statements of income",
              "consolidated statements of cash flows", "consolidated balance sheets",
              "consolidated statements of earning", "consolidated statements of comprehensive earning",
              "consolidated statements of equity", "consolidated statements of stockholders’ equity",
              "consolidated income statement", "consolidated statement of operations",
              "consolidated statement of comprehensive income", "consolidated statement of income",
              "consolidated statement of cash flows", "consolidated balance sheet",
              "consolidated statement of earning", "consolidated statement of comprehensive earning",
              "consolidated statement of equity", "consolidated statement of stockholders’ equity",
              "notes to consolidated", "index for notes"}


def extract_page_num_from_single_line(line):
    # print("start extract sing line page num")
    line_content = line.split(" ")
    # print(line_content)
    if len(line_content) > 0:
        # pageNumber in that line
        if line_content[-1].isnumeric():
            return eval(line_content[-1])
        if re.match(r"[0-9]+-[0-9]+", line_content[-1]) is not None:
            return eval(line_content[-1].split("-")[0])
    return -1


def extract_page_num_from_single_page(current_page):
    # print("start extract single page num")
    page_text = current_page.extract_text()
    if page_text is None:
        return -2
    else:
        page_text = page_text.strip()
        lines = re.split(r'\n+', page_text)
        # lines = page_text.splitlines()
        last_line = lines[-1]
        if "www.sec.gov" in last_line:
            last_line = lines[-2]
        if last_line.strip().isnumeric():
            # print(lastLine)
            return eval(last_line)
        else:
            return -1


def find_actual_page_number(written_page_num):
    # print("start find actual num")
    # print("written is ", written_page_num)
    times = 0
    index = written_page_num - 1
    pdf_len = len(pdf.pages)
    # print(pdf_len)
    prev_empty = False
    while 0 < index < pdf_len and times < pdf_len:
        times += 1
        current_page = pdf.pages[index]
        current_page_num = extract_page_num_from_single_page(current_page)
        # print("current page num(written in doc): ", current_page_num)
        if current_page_num == eval(str(written_page_num)):
            if prev_empty:
                return current_page.page_number - 1
            return current_page.page_number
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


def search_sub_content(item8_page_num, content_page_num):
    # print("start search sub content")
    # print(item8_page_num)
    content_page = pdf.pages[content_page_num - 1]
    # print(content_page.extract_text())
    if "balance sheet" not in content_page.extract_text().lower():  # sub content is in item8 page
        content_page = pdf.pages[item8_page_num - 1]
    # print(content_page.extract_text())
    prev_line = ""
    double_check = False # in case one sentence is split into two lines
    for line in content_page.extract_text().lower().splitlines():
        # print(line)
        if double_check:
            line = prev_line.strip() + line
            double_check = False
        for header in header_set:
            if header in line:
                written_page_num = extract_page_num_from_single_line(line)
                if written_page_num == -1:
                    double_check = True
                    prev_line = line
                else:
                    page_dict[file_name][header] = find_actual_page_number(written_page_num)
                break


def locate_item8():
    global page_dict, key_word
    for page in pdf.pages:
        if page.extract_text() is None:
            continue
        page_text = page.extract_text().lower()
        # print(page_text)
        if key_word in page_text:
            # print(page.page_number)
            # print(page_text)
            # content page found (actual nth page, not the page number written in the document )
            content_page_num = page.page_number
            # split into lines
            lines_in_page = page_text.splitlines()
            # find line of item 8
            for line in lines_in_page:
                # if this line is for item 8
                if key_word in line.lower():
                    item8_written_page_num = extract_page_num_from_single_line(line.lower())
                    actual_item8_page_number = find_actual_page_number(item8_written_page_num)
                    if actual_item8_page_number > 0:
                        this_dict = {
                            "contentPage": page.page_number,  # page index of pdf = contentPage - 1
                            "item8": actual_item8_page_number,
                        }
                        page_dict[file_name] = this_dict
                        search_sub_content(actual_item8_page_number, content_page_num)
                        if len(page_dict[file_name]) < 5:
                            page_dict.pop(file_name)
                            wrong_pdf.append(file_name)
                        else:
                            split_pages()
                    else:
                        wrong_pdf.append(file_name)
                    break
            break


def split_pages():
    pdf_input = PdfFileReader("/home/ubuntu/webserver/uploadedFiles/" + file_name)
    current_pdf_dict = page_dict[file_name]
    for key in current_pdf_dict:
        if key != "contentPage" and key != "item8":
            start_page = current_pdf_dict[key]
            start_key = key
            break

    for key in current_pdf_dict:
        if key == "contentPage" or key == "item8" or key == start_key:
            continue
        pdf_output = PdfFileWriter()
        end_page = current_pdf_dict[key]
        for i in range(start_page, end_page):
            pdf_output.addPage(pdf_input.getPage(i - 1))
        file_title = file_name[:-4]
        pdf_output.write(open("/home/ubuntu/webserver/output/" + file_title+"_"+start_key + ".pdf", 'wb'))
        start_key = key
        start_page = end_page


if __name__ == '__main__':
    # pdf = pdfplumber.open("InputFiles/Skechers_10K_2018.pdf")
    # file_name = "Skechers_10K_2018.pdf"
    # # page = pdf.pages[43]
    # # print(page.extract_text())
    # locate_item8()
    # pdf.close()

    path = "/home/ubuntu/webserver/uploadedFiles"  # dir
    files = os.listdir(path)
    for file in files:
        file_name = file.__str__()
        print(file_name)
        pdf = pdfplumber.open(path + "/" + file)
        locate_item8()
        pdf.close()
    print(page_dict)
    print(wrong_pdf)
