import pydicom
import os


def extract_dicom_metadata(file_path: str):
    if not os.path.exists(file_path):
        return None
    ds = pydicom.dcmread(file_path)
    return {
        "PatientID": ds.get("PatientID"),
        "StudyDate": ds.get("StudyDate"),
        "Modality": ds.get("Modality"),
        "BodyPartExamined": ds.get("BodyPartExamined")
    }

