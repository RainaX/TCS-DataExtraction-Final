from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import pdftotext
import os


pdf_dict = {}
wrong_pdf = []
key_words = ["item 8", "item 9", "item 15"]

def extract_page_num_from_single_line(line):
    # print("start extract sing line page num")
    line_content = line.split(" ")
    if len(line_content) > 0:
        # pageNumber in that line
        if line_content[-1].isnumeric():
            return eval(line_content[-1])
        if re.match(r"[0-9]+-[0-9]+", line_content[-1]) is not None:
            return eval(line_content[-1].split("-")[0])
    return -1

def find_actual_page_number(pdf, written_page_num):
    # print("start find actual num")
    times = 0
    index = written_page_num - 1
    pdf_len = len(pdf)
    prev_empty = False
    while 0 < index < pdf_len and times < pdf_len:
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

def extract_page_num_from_single_page(current_page):
    # print("start extract single page num")
    page_text = current_page
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

def locate_item8(file_name):
    path = "C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\out\\artifacts\\FileUpload_war_exploded\\uploadedFiles\\" + file_name + ".pdf"
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)
    
    global pdf_dict, key_word
    this_dict = {}
    for i in range(len(pdf)):
        page = pdf[i]
        if page is None:
            continue
        page_text = page.lower()
        if key_words[0] in page_text and key_words[1] in page_text:
            lines_in_page = page_text.lower().splitlines()
            number_of_lines = len(lines_in_page)
            index_of_line = 0
            skipped = False

            # Find line of item 8
            for line in lines_in_page:
                if key_words[0] in line:
                    item8_written_page_num = extract_page_num_from_single_line(line)
                    if item8_written_page_num == -1:
                        item8_written_page_num = extract_page_num_from_single_line(lines_in_page[index_of_line + 1])
                        skipped = True
                    actual_item8_page_number = find_actual_page_number(pdf, item8_written_page_num)
                    if skipped:
                        start = index_of_line + 2
                    else:
                        start = index_of_line + 1
                    
                    # Find line of item 9
                    for i in range(start, number_of_lines - 1):
                        if key_words[1] in lines_in_page[i]:
                            item9_written_page_num = extract_page_num_from_single_line(lines_in_page[i])
                            if item9_written_page_num == -1:
                                item9_written_page_num = extract_page_num_from_single_line(lines_in_page[i + 1])
                            actual_item9_page_number = find_actual_page_number(pdf, item9_written_page_num)
                            break
                    break
                index_of_line += 1
            
            # Update dictionary with "start" and "end"
            this_dict["start"] = actual_item8_page_number
            if actual_item9_page_number - actual_item8_page_number >= 30:
                this_dict["end"] = actual_item8_page_number + 30
            else:
                this_dict["end"] = actual_item9_page_number
    
            # If item8 is in item15
            if actual_item9_page_number - actual_item8_page_number <= 1:
                index_of_line = 0
                for line in lines_in_page:
                    if key_words[2] in line:
                        item15_written_page_num = extract_page_num_from_single_line(line)
                        if item15_written_page_num == -1:
                            item15_written_page_num = extract_page_num_from_single_line(lines_in_page[index_of_line + 1])
                        actual_item15_page_number = find_actual_page_number(pdf, item15_written_page_num)
                        this_dict["start"] = actual_item15_page_number
                        this_dict["end"] = len(pdf) + 1
                        break
                    index_of_line += 1

            pdf_dict[file_name] = this_dict
            break

def get_statements_page_num(file_name):
    path = "C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\out\\artifacts\\FileUpload_war_exploded\\uploadedFiles\\" + file_name + ".pdf"
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)

    current_pdf_dict = pdf_dict[file_name]
    start = current_pdf_dict['start']
    end = current_pdf_dict['end']
    
    headers = "consolidated income statements|consolidated statements of operations|consolidated statements of comprehensive income|consolidated statements of income|consolidated statements of cash flows|consolidated balance sheets|consolidated statements of comprehensive earnings|consolidated statements of earning|consolidated statements of comprehensive earning|consolidated statements of earnings|consolidated statements of equity|consolidated statements of stockholders’ equity|consolidated income statement|consolidated statement of operations|consolidated statement of comprehensive income|consolidated statement of income|consolidated statement of cash flows|consolidated balance sheet|consolidated statement of earning|consolidated statement of comprehensive earning|consolidated statement of equity|consolidated statement of stockholders’ equity|consolidated statements of shareholders’ equity|consolidated statements of comprehensive (loss) income|consolidate balance sheets"
    page_endings = "the accompanying notes are an integral part of the consolidated financial statements|see notes to consolidated financial statements|see accompanying notes to consolidated financial statements|the accompanying notes are an integral part of these consolidated financial statements|the accompanying notes are an integral part of these statements|the accompanying notes to the consolidated financial statements are an integral part of these statements|the notes to consolidated financial statements are an integral part of these statements|see accompanying notes"
    table_endings = "notes to consolidated financial statements"

    # Extract text and do the search
    pages_dict = {}
    for i in range(start-1, end-1):
        page = pdf[i]
        lines_in_page = page.splitlines()

        # If reaches "notes to consolidated financial statements", then stops ahead of time
        ifBreak = False
        for line in lines_in_page[0:10]:
            match0 = re.match(table_endings, line.lower().strip())
            if match0 != None:
                ifBreak = True
                break
        if ifBreak == True:
            break
        
        for line in lines_in_page[0:10]:
            match1 = re.search(headers, line.lower().strip())
            if match1 != None:
                table_start_page = i
                table_end_page = -1
                
                # Check the end of the current page
                lines_in_page_strip = page.strip().splitlines()
                for line in lines_in_page_strip:
                    match2 = re.search(page_endings, line.lower())
                    if match2 != None:
                        table_end_page = i
                        break

                # If not, check the end of next page
                if table_end_page == -1 :
                    table_end_page = table_start_page
                    match3 = None
                    while match3 == None and table_end_page - table_start_page <1 and table_end_page < len(pdf)-1: # maximum 2 pages
                        table_end_page += 1
                        for line in pdf[table_end_page].strip().splitlines():
                            match3 = re.search(page_endings, line.lower())
                            if match3 != None:
                                break
                
                # Update to pages_dic
                if table_end_page != -1:
                    if table_start_page in pages_dict.values():
                        # Remove duplicate pages
                        pages_dict = {key:val for key, val in pages_dict.items() if val != table_start_page}
                    pages_dict[table_start_page] = table_end_page
                break
    
    # Update to pdf_dict
    pdf_dict[file_name]['detail_pages'] = pages_dict

    # Split pages based on pages_dict
    for k in pages_dict.keys():
        split_pdf(path, "C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\output\\{}_{}_{}_split.pdf".format(file_name, k, pages_dict[k]), k, pages_dict[k])

# Split a pdf into sub-pdf
def split_pdf(infn, outfn, start_page, end_page):
    pdf_output = PdfFileWriter()
    pdf_input = PdfFileReader(open(infn, 'rb'))
    page_count = pdf_input.getNumPages()

    for i in range(start_page, end_page+1):
        pdf_output.addPage(pdf_input.getPage(i))
    pdf_output.write(open(outfn, 'wb'))


if __name__ == '__main__':
    # Test
    path = r"C:\\Users\\zhang\\OneDrive\\Desktop\\CMUProject_Financial_Data_Extraction\\Webpage\\FileUpload\\out\\artifacts\\FileUpload_war_exploded\\uploadedFiles\\"  # dir
    files = os.listdir(path)
    for i in range(len(files)):
        try:
            file_name = files[i].__str__().split(".")[0]
            if file_name != '':
                print("----Start to download for file {} {}".format(i, file_name))
                locate_item8(file_name)
                get_statements_page_num(file_name)
        except Exception:
            print("****Error in file {} {}****".format(i, file_name))
            continue
    print("Finished all downloading")

