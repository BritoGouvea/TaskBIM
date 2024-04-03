import os
import streamlit as st
import pickle
import pandas as pd
from classes.rules import *

import json

### Funções

def rules_config_tab(rules_config):

    for rule_config in rules_config:
        rule_config.display()

    add_rule_config = st.button('Adicionar conjunto de regras')
    if add_rule_config:
        new_rule_config = RuleConfig()
        new_rule_config.save()
        st.session_state['rules_config'].append(str(new_rule_config.unique_id))
        st.rerun()
    
def pep_expander(item):
    
    rules = st.session_state['PEP'][item]
    with st.expander(item):
        if len(rules) > 0:
            for i, rule in enumerate(rules):
                pep_rule_container(item, i, rule)
        add_button = st.button("Adicionar regra", key=f"add_button-{item}")
        if add_button:
            st.session_state['rules_data']['PEP'][item].append({"Component": None, "Dataframe": None})
        
def pep_rule_container(item: str, index: int, rule):

    columns = ['Propriedade', 'PropertySet', 'Property', 'Operação', 'Valor']
    if rule['Component']:
        component = st.session_state['ifc_elements'].index(rule['Component'])
    else:
        component = None
    if rule['Dataframe']:
        df = pd.DataFrame(rule['Dataframe'], columns = columns)
    else:
        df = pd.DataFrame(columns = columns)
    
    for column in columns:
        df[column] = df[column].astype('str')

    properties = ['Name', 'Description', 'Type', 'Material','PropertySet']
    operation = ['Exato', 'Contém', 'Começa com', 'Termina com']
    config = {
        'Propriedade': st.column_config.SelectboxColumn('Propriedade', options=properties),
        'Operação': st.column_config.SelectboxColumn('Operação', options=operation)
    }
    with st.container(border=True):
        cols = st.columns(3)
        with cols[0]:
            component = st.selectbox(
                "Componente", 
                st.session_state['ifc_elements'], 
                index=component, 
                placeholder="Escolha um tipo de elemento IFC...",
                key=f"selectbox-{item}_{index}"
                )
        data = st.data_editor(
            df, 
            column_config=config, 
            use_container_width=True,
            num_rows='dynamic',
            key=f"dataframe-{item}_{index}",
            )
        json_dataframe = json.loads(data.to_json(orient='records'))
        json_data = {"Component": component, "Dataframe": json_dataframe}
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.button("Salvar regra", key=f"save_button-{item}-{index}")
            if save_button:
                st.session_state['rules_data']['PEP'][item][index] = json_data
                with open('./assets/regras.json', 'w') as f:
                    json.dump(st.session_state['rules_data'], f, ensure_ascii=False, indent=4)
                st.rerun()
        with col2:
            delete_button = st.button("Deletar regra", key=f"delete_button-{item}_{index}")
            if delete_button:
                del st.session_state['rules_data']['PEP'][item][index]
                with open('./assets/regras.json', 'w') as f:
                    json.dump(st.session_state['rules_data'], f, ensure_ascii=False, indent=4)
                st.rerun()

### Layout

def main():

    ### Loading data

    if 'rules_config' not in st.session_state:
        st.session_state['rules_config'] = [
            rule_config.removesuffix('.ruleconfig') 
            for rule_config in os.listdir('./rules') 
            if rule_config.endswith('.ruleconfig')
        ]
    
    rules_config = []
    tabs_name = ['GERAL']
    if st.session_state['rules_config']:
        for rule_config in st.session_state['rules_config']:
            rule_config: RuleConfig = pickle.load(open(f'./rules/{rule_config}.ruleconfig', 'rb'))
            rules_config.append(rule_config)
        rule_config_names = [ rule_config.rule_name for rule_config in rules_config ]
        tabs_name.extend(rule_config_names)

    if 'PEP' not in st.session_state:
        regras = json.load(open("./assets/regras.json"))
        st.session_state['PEP'] = regras['PEP']

    ifc_elements = json.load(open('./assets/ifc_elements.json'))
    if 'ifc_elements' not in st.session_state:
        st.session_state['ifc_elements'] = ifc_elements
    
    ### Layout
    st.title("Regras")
    
    tabs = st.tabs(tabs_name)

    with tabs[tabs_name.index('GERAL')]:
        rules_config_tab(rules_config)

    for i, rule_config in enumerate(rules_config):
        with tabs[i + 1]:
            if rule_config.rule:
                rule_config.rule.display()
                tab_save_button = st.button('Salvar', type='primary', key=f'{rule_config.rule_name}_tab_save')
                if tab_save_button:
                    rule_config.save()

if __name__ == '__main__':
        
    # Init layout
    main()