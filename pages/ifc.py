import streamlit as st
from classes.primavera_xml import Plan
from uuid import uuid4

if 'ifcs' not in st.session_state:
    st.session_state['ifcs'] = None
if 'xml' not in st.session_state:
    st.session_state['xml'] = None

plan: Plan = list(st.session_state['xml'].values())[0]
ActivityCodes = {}
for ActivityCodeType in plan.ActivityCodeTypes.values():
    key = ActivityCodeType.Name
    values = [ActivityCode.Description for ActivityCode in ActivityCodeType.ActivityCodes]
    ActivityCodes.update({key: values})

st.title('IFC')

for identifier, ifc in st.session_state['ifcs'].items():
    with st.container(border=True):
        st.write(f"**{identifier}**")
        if ifc['params']:
            for key, value in ifc['params'].items():
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    activity_code_type = st.selectbox('ActivityCodeType', options=ActivityCodes.keys(), key=f'{uuid4()}_act')
                with col2:
                    activity_code = st.selectbox('ActivityCode', options=ActivityCodes[activity_code_type], key=f'{uuid4()}_ac')
        add_param = st.button('Adicionar ActivityCode global', key=f'{identifier}_add')
        if add_param:
            st.session_state['ifcs'][identifier]['params'] = {'ActivityCode': None}
