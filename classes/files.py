import tempfile
import ifcopenshell
from classes.primavera_xml import Plan

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
    with tempfile.NamedTemporaryFile(suffix=".ifc") as tmp_file:
        tmp_file.write(bytes)
        file = Plan(tmp_file.name)
        return file