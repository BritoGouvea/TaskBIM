import streamlit as st
from classes.primavera_xml import Plan
import pickle
import ifcopenshell
from classes.ifc_functions import property_mapping

if 'ifcs' not in st.session_state:
    st.session_state['ifcs'] = None
if 'xml' not in st.session_state:
    st.session_state['xml'] = None

st.title('IFC')

if not st.session_state['ifcs']:
    st.warning("Necessário carregar os modelos em IFC ou IFCZIP", icon="⚠️")
    st.stop()

if st.session_state['xml']:
    plan: Plan = list(st.session_state['xml'].values())[0]
    activity_codes = {}
    for activity_code_type in plan.ActivityCodeTypes.values():
        key = activity_code_type.Name
        values = [activity_code.Description for activity_code in activity_code_type.ActivityCodes]
        activity_codes.update({key: values})
    activity_code_types = st.multiselect(
        'Selecione os Activity Code Types que se aplicam a todos elementos do modelo',
        options=[ Activity for Activity in activity_codes.keys() ]
    )
else:
    st.warning("Necessário carregar o planejamento em XML", icon="⚠️")

for identifier, ifc in st.session_state['ifcs'].items():
    with st.expander(f'**{identifier}**'):
        for activity_code_type in activity_code_types:
            if activity_code_type in ifc['params']:
                value = ifc['params'][activity_code_type]
            else:
                ifc['params'].update({activity_code_type: None})
        if activity_code_types:
            for activity_code_type, col in zip(activity_code_types, st.columns(len(activity_code_types))):
                with col:
                    ifc['params'][activity_code_type] = st.selectbox(
                        activity_code_type,
                        options=activity_codes[activity_code_type],
                        key=f'{identifier}_param_{activity_code_type}'
                    )