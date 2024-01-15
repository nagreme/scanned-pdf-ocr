import pdf2image
from PyPDF2 import PdfWriter
import pytesseract as pytess
import argparse
import os
import logging
import shutil


EXT_PDF = '.pdf'
EXT_TXT = '.txt'
PAGES_FOLDER = "./temp_pdf_output_pages/"

logging.basicConfig(level=logging.INFO)


def main(args):
    # can't OCR pdf pages so I convert to images first
    # there's likely some data loss, we can probably do better...
    logging.info("Converting pdf to images")
    doc = pdf2image.convert_from_path(args.input)
    pdf = []
    txt = ""
    
    logging.info("Starting OCR")
    
    # extract text from each page image
    for page_number, page_data in enumerate(doc):
        # +1 for one index instead of zero index
        logging.info(f"Page number: {page_number+1} of {len(doc)}")
        # accumulate text
        txt += f"\n<page {page_number}>\n" + pytess.image_to_string(page_data)
        # accumulate pdf data
        pdf.append(pytess.image_to_pdf_or_hocr(page_data))
            
    # write text
    logging.info("Writing text")
    with open(args.output + EXT_TXT, 'w') as f:
        f.write(txt)
    
    # setup temp dir
    os.makedirs(PAGES_FOLDER, exist_ok=True)
    
    # write each pdf page
    logging.info("Writing pdf pages")
    for page_num, page_data in enumerate(pdf):
        filename = f"{PAGES_FOLDER}page_{str(page_num)}{EXT_PDF}"
        with open(filename, 'wb') as f:
            f.write(page_data) 
        
    # re-assemble pdf
    logging.info("Re-assembling PDF")
    merger = PdfWriter()
    for i in range(len(pdf)):
        merger.append(f"{PAGES_FOLDER}page_{str(i)}{EXT_PDF}")
    
    merger.write(args.output + EXT_PDF)
    merger.close()
    
    logging.info("Cleaning up pages dir")
    shutil.rmtree(PAGES_FOLDER)
    
    logging.info("Extraction complete")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Python OCR')
    parser.add_argument('--input', help='Input PDF file', action='store')
    parser.add_argument('--output', help='Output file name', action='store')
    main(parser.parse_args())