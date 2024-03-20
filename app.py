import streamlit as st
from task_reader import primavera
import ifc_classification.system_classification as sc
from classes.rules import *

st.set_page_config(
    page_title='TaskBIM',
    layout='wide'
)

st.title('TaskBIM')

col1, col2 = st.columns(2)

with col1:
    st.subheader("IFC")
    ifc_files = st.file_uploader("Upload de arquivos .IFC", type='ifc', accept_multiple_files=True)
with col2:
    st.subheader("PRIMAVERA-XML")
    xml_files = st.file_uploader("Upload de arquivos .XML", type='xml')

if st.button("Processar"):
    for ifc_file in ifc_files:
        ifc_model = sc.process_classification(ifc_file)
    try:
        BuildingStory = ifc_model.by_type('IfcBuildingStorey')
        st.write(BuildingStory)
    except:
        st.write("Necessário carregar modelo")