import streamlit as st
import pickle
import uuid
import os
from pandas import DataFrame

class RuleConfig:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.rule_name: str = ""
        self.rule_type = None
        self.values: list = []

    def __repr__(self) -> str:
        name = self.rule_name if self.rule_name else ""
        return "<" + str(self.unique_id) + "-" + name + ">"

    def display(self) -> None:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 3, 0.5, 0.5])
            with col1:
                self.rule_name = st.text_input(
                    "Nome da regra",
                    value=self.rule_name,
                    label_visibility='collapsed',
                    placeholder='Nome da regra',
                    key=f'{self.unique_id}_rule_name'
                )
            with col2:
                options = ('Filtro de elementos', 'Entidade IFC', 'Mapeamento de propriedade')
                self.rule_type = st.selectbox(
                    label="Tipo da regra",
                    options=options,
                    index=options.index(self.rule_type) if self.rule_type else None,
                    placeholder='Escolha uma opção',
                    label_visibility='collapsed',
                    key=f'{self.unique_id}_rule_type'
                )
            with col3:
                save_button = st.button('Salvar', key=f'{self.unique_id}_save')
            with col4:
                with st.popover("Deletar"):
                    st.write("Você tem certeza que quer deletar?")
                    delete_button = st.button('Sim', type='primary', key=f'{self.unique_id}_delete')

            df = DataFrame(self.values, columns = ['Classificação'])
            with st.expander("Itens"):
                dataframe = st.data_editor(
                        data=df,
                        num_rows='dynamic',
                        use_container_width=True,
                        hide_index=True,
                        key=f'{self.unique_id}_df_values'
                    )
                self.values = dataframe.to_dict(orient='records')
            if save_button:
                self.save()
            if delete_button:
                self.delete()
    
    def save(self):
        with open(f'./rules/{str(self.unique_id)}.ruleconfig', 'wb') as file:
            pickle.dump(self, file)
        st.toast("Salvo com sucesso", icon='🎉')

    def delete(self):
        st.session_state['rules_config'].remove(str(self.unique_id))
        os.remove(f'./rules/{str(self.unique_id)}.ruleconfig')
        st.rerun()

class PropertyMapping:

    def __init__(self, rule_config) -> None:
        self.unique_id = uuid.uuid4()
        self.rule_config: RuleConfig = rule_config
        self.map_to_same_property: bool = True
        self.ifc_entities = []
        self.origin_property = None
        self.destiny_property = None
        self.values = None

    def display(self) -> None:

        cols = st.columns(2)

        attribute_options = ['Name', 'Description', 'Type', 'Material','PropertySet']
        
        with cols[0]:

            col1, col2, col3 = st.columns(3)

            with col1:
                origin_attribute = st.selectbox("Atributo", attribute_options)
                if origin_attribute == 'PropertySet':
                    origin_disabled = True
                else:
                    origin_disabled = False
            with col2:
                origin_pset = st.text_input("PropertySet", disabled=origin_disabled)
            with col3:
                origin_property = st.text_input("Property", disabled=origin_disabled)
                
                    

class ElementFilter:

    def __init__(self, rule_config) -> None:
        self.unique_id = uuid.uuid4()
        self.rule_config: RuleConfig = rule_config