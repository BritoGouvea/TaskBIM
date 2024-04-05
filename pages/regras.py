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
    
    ### Layout
    col1, col2 = st.columns([10, 1])
    with col1:
        st.title("Regras")
    with col2:
        rule_save_button = st.button('Salvar', key='rule_save_button', use_container_width=True, type='primary')
    tabs = st.tabs(tabs_name)

    with tabs[tabs_name.index('GERAL')]:
        rules_config_tab(rules_config)

    for i, rule_config in enumerate(rules_config):
        with tabs[i + 1]:
            if rule_config.rule:
                rule_config.rule.display()
    
    if rule_save_button:
        for rule_config in rules_config:
            rule_config.save()

if __name__ == '__main__':
        
    # Init layout
    main()