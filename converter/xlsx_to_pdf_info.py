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
    excel.DisplayAlerts = False

    try:
        workbook = excel.Workbooks.Open(os.path.abspath(xlsx_path))
        workbook.ExportAsFixedFormat(
            Type=0,
            Filename=pdf_path,
            Quality=0,
            IncludeDocProperties=True,
            IgnorePrintAreas=False,
            OpenAfterPublish=False,
        )
        print(f"PDF 저장 완료: {pdf_path}")

    except Exception as e:
        print(f"PDF 변환 실패: {e}")
        raise

    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()
        del workbook
        del excel

    return {"filename": pdf_filename, "path": f"data/pdf/{pdf_filename}"}
