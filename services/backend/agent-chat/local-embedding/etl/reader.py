import pdfplumber
import pytesseract
import traceback

from multiprocessing import Pool
from pdf2image import convert_from_path


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


def _extract_pdf_text_ocr(filepath) -> list[str]:
    images = convert_from_path(filepath)
    with Pool(processes=8) as pool:
        pages = pool.map(pytesseract.image_to_string, images)
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
