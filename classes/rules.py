import streamlit as st
import pickle
import uuid
import os
from pandas import DataFrame
from classes.ifc import IfcEntity

class RuleConfig:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.rule_name: str = ""
        self.rule_type = None
        self.values: list = []
        self.rule = None

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
                if self.rule_type:
                    self.rule_mapping()
            with col3:
                save_button = st.button('Salvar', key=f'{self.unique_id}_save')
            with col4:
                with st.popover("Deletar"):
                    st.write("Você tem certeza que quer deletar?")
                    delete_button = st.button('Sim', type='primary', key=f'{self.unique_id}_delete')

            df = DataFrame(self.values, columns = ['Classificação'])
            with st.expander("Itens"):
                if self.rule_type:
                    dataframe = st.data_editor(
                            data=df,
                            num_rows='dynamic',
                            use_container_width=True,
                            hide_index=True,
                            key=f'{self.unique_id}_df_values'
                        )
                    self.values = dataframe.to_dict(orient='records')
                    self.rule.classification_items = [ item['Classificação'] for item in self.values ]
            if save_button:
                self.save()
            if delete_button:
                self.delete()
    
    def rule_mapping(self):
        mapping = {
            'Filtro de elementos': ElementFilter(),
            'Entidade Ifc': PropertyMapping(),
            'Mapeamento de propriedade': PropertyMapping()
        }
        if not self.rule:
            self.rule = mapping[self.rule_type]
        
    
    def save(self):
        with open(f'./rules/{str(self.unique_id)}.ruleconfig', 'wb') as file:
            pickle.dump(self, file)
        st.toast("Salvo com sucesso", icon='🎉')

    def delete(self):
        st.session_state['rules_config'].remove(str(self.unique_id))
        os.remove(f'./rules/{str(self.unique_id)}.ruleconfig')
        st.rerun()

class PropertyMapping:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.classification_items: list = None
        self.ifc_entity_type: str = None
        self.ifc_entities: list = []
        self.map_to_same_property: bool = False
        self.map_with_same_value: bool = False
        self.origin_property: tuple = None
        self.destiny_property: tuple = None
        self.values = None

    def display(self) -> None:
        
        ifc_entity_type_options = ['IfcElement', 'IfcSpatialElement']
        attribute_options = ['Name', 'Description', 'Type', 'Material','PropertySet']

        col1, col2 = st.columns([1, 5])
        with col1:
            self.ifc_entity_type = st.selectbox(
                label="Tipo da entidade IFC",
                options=ifc_entity_type_options,
                placeholder='Selecione o tipo de entidade IFC',
                index=ifc_entity_type_options.index(self.ifc_entity_type) if self.ifc_entity_type else None,
                label_visibility='collapsed',
                key=f"{self.unique_id}_ifc_entity_type_options"
            )
        with col2:
            self.ifc_entities = st.multiselect(
                "Selecione as IfcEntities para alterar",
                options=IfcEntity.ifc_entity().find_subclass(self.ifc_entity_type).list_all_subclasses() if self.ifc_entity_type else [],
                default=self.ifc_entities,
                placeholder='Selecione as entidades IFC',
                label_visibility='collapsed',
                key=f'{self.unique_id}_ifc_entities'
            )
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            self.map_to_same_property = st.checkbox(
                "Mapear para o mesmo atributo",
                value=self.map_to_same_property,
                key=f'{self.unique_id}_map_to_same_property'
            )
        with col2:
            self.map_with_same_value = st.checkbox(
                "Copiar o valor",
                value=self.map_with_same_value,
                disabled=self.map_to_same_property,
                key=f'{self.unique_id}_map_with_same_value'
            )
        cols = st.columns(6)
        with cols[0]:
            origin_attrib = st.selectbox(
                'Atributo origem',
                attribute_options,
                index=attribute_options.index(self.origin_property[0]),
                key=f'{self.unique_id}_origin_attrib'
            )
        with cols[1]:
            origin_pset = st.text_input(
                'PropertySet origem',
                value=self.origin_property[1],
                disabled=origin_attrib != 'PropertySet',
                key=f'{self.unique_id}_origin_pset'
            )
        with cols[2]:
            origin_prop = st.text_input(
                'Property origem',
                value=self.origin_property[2],
                disabled=origin_attrib != 'PropertySet',
                key=f'{self.unique_id}_origin_prop'
            )
        self.origin_property = (origin_attrib, origin_pset, origin_prop)
        with cols[3]:
            destiny_attrib = st.selectbox(
                'Atributo Destino',
                attribute_options,
                index=attribute_options.index(self.destiny_property[0]),
                disabled=self.map_to_same_property,
                key=f'{self.unique_id}_destiny_attrib'
            )
        with cols[4]:
            destiny_pset = st.text_input(
                'PropertySet destino',
                value=self.destiny_property[1],
                disabled=destiny_attrib != 'PropertySet',
                key=f'{self.unique_id}_destiny_pset'
            )
        with cols[5]:
            destiny_prop = st.text_input(
                'Property destino',
                value=self.destiny_property[2],
                disabled=destiny_attrib != 'PropertySet',
                key=f'{self.unique_id}destiny_prop'
            )
        self.destiny_property = (destiny_attrib, destiny_pset, destiny_prop)
        
        if not self.map_with_same_value:
            df = DataFrame(self.values, columns = ['Valor modelo', 'Classificação'])
            column_config = {
                "Classificação": st.column_config.SelectboxColumn(
                    "Item da classificação",
                    options=self.classification_items,
                    required=True
                )
            }
            with st.expander("Valores"):
                dataframe = st.data_editor(
                        data=df,
                        num_rows='dynamic',
                        column_config=column_config,
                        use_container_width=True,
                        hide_index=True,
                        key=f'{self.unique_id}_df_values'
                    )
                self.values = dataframe.to_dict(orient='records')

class ElementFilter:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.classification_items: list = None
        self.filter_rules: dict = {}

    def display(self) -> None:

        ifc_products = IfcEntity.ifc_entity().find_subclass('IfcProduct').list_all_subclasses()
        ifc_products.sort()
        properties = ['Name', 'Description', 'Type', 'Material','PropertySet']
        operation = ['Exato', 'Contém', 'Começa com', 'Termina com']
        config = {
            'IfcEntity': st.column_config.SelectboxColumn('IfcEntity', options=ifc_products),
            'Propriedade': st.column_config.SelectboxColumn('Propriedade', options=properties),
            'Operação': st.column_config.SelectboxColumn('Operação', options=operation)
        }

        for item in self.classification_items:
            with st.expander(item):
                if item in self.filter_rules:
                    df = DataFrame(self.filter_rules[item])
                else:
                    df = DataFrame(columns=['IfcEntity', 'Propriedade', 'PropertySet', 'Property', 'Operação', 'Valor'])
                dataframe = st.data_editor(
                    df,
                    column_config=config,
                    use_container_width=True,
                    num_rows='dynamic',
                    key=f'{self.unique_id}_{item}_dataeditor'
                )
                if not dataframe.empty:
                    self.filter_rules[item] = dataframe.to_dict(orient='records')
                if dataframe.empty and item in self.filter_rules:
                    st.write('vazio')
                    self.filter_rules.pop(item)