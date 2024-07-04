import tempfile
from collections import Counter
import ifcopenshell
from classes.primavera_xml import Plan
import zipfile
import io

def open_ifc_in_memory(uploaded_file):
    # Read the file as bytes
    bytes = uploaded_file.read()
    # """Opens an IFC file in memory using a temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".ifc") as tmp_file:
        tmp_file.write(bytes)
        file = ifcopenshell.open(tmp_file.name)
        return file
  
def open_xml_in_memory(uploaded_file):
    # Read the file as bytes
    bytes = uploaded_file.read()
    # """Opens an IFC file in memory using a temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".xml") as tmp_file:
        tmp_file.write(bytes)
        file = Plan(tmp_file.name)
        return file
    
def check_duplicates(list_to_check):
    counts = Counter(list_to_check)
    duplicates = [item for item, count in counts.items() if count > 1]
    return duplicates

def create_zip_from_ifc_files(ifc_files_dict):
    # Create a bytes buffer to hold the zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, file_info in ifc_files_dict.items():
            ifc_file = file_info["file"]
            # Create a temporary file to write the IFC content
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp_file:
                ifc_file.write(tmp_file.name)
                tmp_file.seek(0)  # Move to the beginning of the file
                # Read the file and write it to the zip file
                with open(tmp_file.name, 'rb') as f:
                    zip_file.writestr(file_name, f.read())
    
    # Ensure the buffer is ready for reading
    zip_buffer.seek(0)
    return zip_buffer