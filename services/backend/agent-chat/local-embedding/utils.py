import os
import fitz  # PyMuPDF
import pandas as pd
import pdfplumber
import pytesseract
import traceback

from pdf2image import convert_from_path
from PIL import Image


def _extract_pdf_text_ocr(filepath) -> list[str]:
    images = convert_from_path(filepath)
    pages = [pytesseract.image_to_string(img) for img in images]

    return pages


def _extract_pdf_content_by_pdfplumber(filepath) -> list[dict]:
    page_results = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            extracted_tables = []
            tables = page.extract_tables()
            page_text = page.extract_text()
            for i, table in enumerate(tables):
                table_content = []

                headers = table[0]
                rows = table[1:]

                for row in rows:
                    row_text = ", ".join(f"{headers[i]}: {row[i]}" for i in range(len(row)))  # noqa
                    table_content.append(row_text)

                table_str = f"Table {i} content:\n" + "\n".join(table_content)
                extracted_tables.append(table_str)

            tables_str = "\n\n".join(extracted_tables)

            page_results.append({
                "tables": tables_str,
                "text": page_text
            })

    return page_results


def prepare_pdf_content(filepath: str) -> list[dict]:
    try:
        pdfplumber_pages = _extract_pdf_content_by_pdfplumber(filepath)
        ocr_pages = _extract_pdf_text_ocr(filepath)
        pages = [
            {
                "pdfplumber": pdfplumber_result,
                "ocr_text": orc_text
            }
            for pdfplumber_result, orc_text in zip(pdfplumber_pages, ocr_pages)
        ]

        return pages
    except Exception as e:
        traceback.print_exc()
        print("ERR:", e)
        return None


def extract_text_from_pdf(pdf_path):
    text_pages = []

    # Try extracting text from normal PDFs
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            page_number += 1

            extracted_text = page.extract_text()

            img = page.to_image().original  # Extract image of the page
            extracted_text_ocr = pytesseract.image_to_string(img)  # OCR

            final_text = f"""# PAGE METADATA START #
document page: {page_number}\n
# PAGE METADATA END #
# PAGE CONTENT START #
{extracted_text}
## OCR CONTENT START ##
{extracted_text_ocr}
## OCR CONTENT END ##
# PAGE CONTENT END #
"""
            text_pages.append(final_text)

    return text_pages


def extract_text_from_pdf_depr(pdf_path):
    text_pages = []
    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc):
            page_number += 1
            text = page.get_text("text")
            final_text = f"""### PAGE METADATA START
document page: {page_number}\n
### PAGE METADATA END
### PAGE CONTENT
{text}
### PAGE CONTENT END
"""
            text_pages.append(final_text)
    return text_pages


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {image_path}: {e}")
        return ""


def extract_text(file_path) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    # elif ext in [".png", ".jpeg", ".jpg"]:
    #     return [extract_text_from_image(file_path)]
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return [f.read()]
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        return [df.to_string()]
    else:
        return None  # Unsupported formats return empty text
