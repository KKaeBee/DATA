import os
import pythoncom
import win32com.client


def convert_xlsx_to_pdf(xlsx_path: str, output_dir: str) -> dict:
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"파일 없음: {xlsx_path}")
    os.makedirs(output_dir, exist_ok=True)

    filename_wo_ext = os.path.splitext(os.path.basename(xlsx_path))[0]
    pdf_filename = filename_wo_ext + ".pdf"
    pdf_path = os.path.abspath(os.path.join(output_dir, pdf_filename))

    pythoncom.CoInitialize()
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    try:
        wb = excel.Workbooks.Open(xlsx_path)
        wb.ExportAsFixedFormat(0, pdf_path)
        wb.Close(False)
        print(f"PDF 저장 완료: {pdf_path}")

    except Exception as e:
        print(f"PDF 변환 실패: {e}")
        raise

    finally:
        excel.Quit()

    return "", {
        "filename": pdf_filename,
        "path": f"pdf/{pdf_filename}"
    }
