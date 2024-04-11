import os
import streamlit as st
import pickle
import pandas as pd
from classes.rules import *

import json

def main():

    ### Loading data

    if 'ruleset' not in st.session_state:
        st.warning('Ainda não há nenhum conjunto de regras crie o seu primeiro conjunto ou faça o upload na página incial do app', icon='⚠️')
        st.stop()
    else:
        if not st.session_state['ruleset']:
            st.warning('Ainda não há nenhum conjunto de regras crie o seu primeiro conjunto ou faça o upload na página incial do app', icon='⚠️')
            st.stop()
        else:
            ruleset: Ruleset = pickle.load(open(f'./rules/{st.session_state.ruleset}.ruleset', 'rb'))

    ### Layout
    col1, col2 = st.columns([10, 1])
    with col1:
        st.title(st.session_state['ruleset'])
    with col2:
        rule_save_button = st.button('Salvar', key='rule_save_button', use_container_width=True, type='primary')
    
    tabs_name = ['GERAL']
    rule_config_names = [ rule_config.rule_name if rule_config.rule_name else "Sem nome"
                         for rule_config in ruleset.rules ]
    tabs_name.extend(rule_config_names)
    tabs = st.tabs(tabs_name)

    with tabs[tabs_name.index('GERAL')]:
        ruleset.display()


    for i, rule_config in enumerate(ruleset.rules):
        with tabs[i + 1]:
            if rule_config.rule:
                rule_config.rule.display()
    
    if rule_save_button:
        ruleset.save()

if __name__ == '__main__':
    
    # Init layout
    main()