import streamlit as st
from task_reader import primavera
import ifc_classification.system_classification as sc
from classes.rules import *
from classes.files import *

st.set_page_config(
    page_title='TaskBIM',
    layout='wide'
)

if 'ifcs' not in st.session_state:
    st.session_state['ifcs'] = None
if 'xml' not in st.session_state:
    st.session_state['xml'] = None

st.title('TaskBIM')

col1, col2 = st.columns(2)

with col1:
    st.subheader("IFC")
    ifc_files = st.file_uploader("Upload de arquivos .IFC", type='ifc', accept_multiple_files=True)
    if not ifc_files:
        try:
            if st.session_state['ifcs']:
                st.write(list(st.session_state['ifcs'].keys()))
        except:
            pass
with col2:
    st.subheader("PRIMAVERA-XML")
    xml_file = st.file_uploader("Upload de arquivos .XML", type='xml')
    if not xml_file:
        try:
            st.write(list(st.session_state['xml'].keys()))
        except:
            pass

if not st.session_state['ifcs']:
    try:
        st.session_state['ifcs'] = { ifc_file.name: {'file': open_ifc_in_memory(ifc_file), 'params': None}  for ifc_file in ifc_files }
    except:
        pass
if not st.session_state['xml']:
    try:
        st.session_state['xml'] = { xml_file.name: open_xml_in_memory(xml_file) if xml_file else None }
    except:
        pass

# if st.button("Processar"):
#     for ifc_file in ifc_files:
#         ifc_model = sc.process_classification(ifc_file)
#     try:
#         BuildingStory = ifc_model.by_type('IfcBuildingStorey')
#         st.write(BuildingStory)
#     except:
#         st.warning("Necessário carregar modelo")