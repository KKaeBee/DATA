import os
import pythoncom
import win32com.client


def convert_hwp_to_pdf(hwp_path: str, output_dir: str) -> dict:
    if not os.path.exists(hwp_path):
        raise FileNotFoundError(f"파일 없음: {hwp_path}")
    os.makedirs(output_dir, exist_ok=True)

    filename_wo_ext = os.path.splitext(os.path.basename(hwp_path))[0]
    pdf_filename = filename_wo_ext + ".pdf"
    pdf_path = os.path.abspath(os.path.join(output_dir, pdf_filename))

    pythoncom.CoInitialize()
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckDLL")

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FileAuto")
        hwp.XHwpWindows.Item(0).Visible = False
        hwp.Open(hwp_path)

        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

        print(f"PDF 저장 완료: {pdf_path}")

    except Exception as e:
        print(f"PDF 변환 실패: {e}")
        raise

    finally:
        hwp.Quit()
        del hwp

    return "", {"filename": pdf_filename, "path": f"data/pdf/{pdf_filename}"}
