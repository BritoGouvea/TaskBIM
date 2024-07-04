import streamlit as st
from classes.primavera_xml import Plan
import pickle
import ifcopenshell
from classes.ifc_functions import property_mapping
from classes.files import create_zip_from_ifc_files

if 'ifcs' not in st.session_state:
    st.session_state['ifcs'] = None
if 'xml' not in st.session_state:
    st.session_state['xml'] = None

st.title('IFC')

if not st.session_state['ifcs']:
    st.warning("Necessário carregar os modelos em IFC ou IFCZIP", icon="⚠️")
    st.stop()

if st.session_state['xml']:
    if 'global_activity_codes' not in st.session_state:
        st.session_state['global_activity_codes'] = None
        global_activity_codes = None
    else:
        global_activity_codes = st.session_state['global_activity_codes']
    plan: Plan = list(st.session_state['xml'].values())[0]
    activity_codes = {}
    for activity_code_type in plan.ActivityCodeTypes.values():
        key = activity_code_type.Name
        values = [activity_code.Description for activity_code in activity_code_type.ActivityCodes]
        activity_codes.update({key: values})
    activity_code_types = st.multiselect(
        'Selecione os Activity Code Types que se aplicam a todos elementos do modelo',
        options=[ Activity for Activity in activity_codes.keys() ],
        default= global_activity_codes
    )
    st.session_state['global_activity_codes'] = activity_code_types
else:
    st.warning("Necessário carregar o planejamento em XML", icon="⚠️")
    st.stop()

for identifier, ifc in st.session_state['ifcs'].items():
    with st.expander(f'**{identifier}**'):
        if activity_code_types:
            selected_activity_codes = {}
            for activity_code_type, col in zip(activity_code_types, st.columns(len(activity_code_types))):
                if activity_code_type not in ifc['activity_codes']:
                    ifc['activity_codes'][activity_code_type] = None
                    value = None
                else:
                    value = ifc['activity_codes'][activity_code_type]
                with col:
                    selected_activity_code = st.selectbox(
                        activity_code_type,
                        options=activity_codes[activity_code_type],
                        key=f'{identifier}_param_{activity_code_type}',
                        index=activity_codes[activity_code_type].index(value) if value else 0
                    )
                    selected_activity_codes[activity_code_type] = selected_activity_code
            st.session_state['ifcs'][identifier]['activity_codes'] = selected_activity_codes

process_button = st.button('Processar')

if st.session_state['ifcs']:
    zip_buffer = create_zip_from_ifc_files(st.session_state['ifcs'])
    st.download_button(
        label="Download ZIP",
        data=zip_buffer,
        file_name="ifc_files.zip",
        mime="application/zip"
    )