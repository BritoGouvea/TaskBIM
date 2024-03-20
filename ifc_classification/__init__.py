import tempfile
import ifcopenshell

def open_ifc_in_memory(uploaded_file):
  # Read the file as bytes
  ifc_bytes = uploaded_file.read()
  # """Opens an IFC file in memory using a temporary file."""
  with tempfile.NamedTemporaryFile(suffix=".ifc") as tmp_file:
    tmp_file.write(ifc_bytes)
    ifc_model = ifcopenshell.open(tmp_file.name)
    return ifc_model