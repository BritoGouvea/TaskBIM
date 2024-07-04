import streamlit as st
import ifc_classification.system_classification as sc
from classes.rules import *
from classes.files import *

st.set_page_config(
    page_title='TaskBIM',
    layout='wide'
)

# Initial session state

if 'ifcs' not in st.session_state:
    st.session_state['ifcs'] = None
if 'xml' not in st.session_state:
    st.session_state['xml'] = None
if 'ruleset' not in st.session_state:
    st.session_state['ruleset'] = None
if 'rulesets' not in st.session_state:
    st.session_state['rulesets'] = [
        rule_config.removesuffix('.ruleset') 
        for rule_config in os.listdir('./rules') 
        if rule_config.endswith('.ruleset')
    ]

# Layout

st.title('TaskBIM')

col1, col2 = st.columns(2)

with col1:
    st.subheader("IFC")
    ifc_files = st.file_uploader("Upload de arquivos .IFC", type=['ifc', 'ifczip'], accept_multiple_files=True, label_visibility="collapsed")
    if not ifc_files:
        try:
            if st.session_state['ifcs']:
                st.write(list(st.session_state['ifcs'].keys()))
        except:
            pass
with col2:
    st.subheader("PRIMAVERA-XML")
    xml_file = st.file_uploader("Upload de arquivos .XML", type='xml', label_visibility="collapsed")
    if not xml_file:
        try:
            st.write(list(st.session_state['xml'].keys()))
        except:
            pass

if not st.session_state['ifcs']:
    try:
        st.session_state['ifcs'] = { ifc_file.name: {'file': open_ifc_in_memory(ifc_file),
                                                     'activity_codes': {},
                                                     }  for ifc_file in ifc_files }
    except:
        pass
if not st.session_state['xml']:
    try:
        st.session_state['xml'] = { xml_file.name: open_xml_in_memory(xml_file) if xml_file else None }
    except:
        pass

st.subheader('RULESETS')

if not st.session_state['rulesets']:
    st.warning('Ainda não há nenhum conjunto de regras crie o seu primeiro conjunto ou faça o upload', icon='⚠️')
create_ruleset_button = False
col1, col2 = st.columns(2) 
with col1:
    colA, colB = st.columns([2,1])
    with colA:
        ruleset_name = st.text_input(
            'Escolha um nome para sua regra',
            placeholder='Escolha um nome para sua regra',
            label_visibility='collapsed'        )
    with colB:
        create_ruleset_button = st.button('Criar este conjunto',
                                          use_container_width=True,
                                          disabled=False if ruleset_name else True)
        if create_ruleset_button:
            if ruleset_name not in st.session_state['rulesets']:
                st.session_state['rulesets'].append(ruleset_name)
    with colA:
        ruleset_choice = st.selectbox('Escolha o conjunto de regras a ser aplicado',
                            index=st.session_state['rulesets'].index(st.session_state['ruleset']) if st.session_state['ruleset'] else None,
                            options=st.session_state['rulesets'],
                            label_visibility='collapsed'
                            )
    with colB:
        select_ruleset_button = st.button('Aplicar ruleset',
                                          use_container_width=True,
                                          disabled=False if ruleset_choice else True)
with col2:
    st.file_uploader('Suba seu conjunto de regras', label_visibility='collapsed')

if create_ruleset_button:
    ruleset = Ruleset(ruleset_name)
    ruleset.save()

if select_ruleset_button:
    st.session_state['ruleset'] = ruleset_choice
