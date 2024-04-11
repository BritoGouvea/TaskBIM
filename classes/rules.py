import streamlit as st
import pickle
import uuid
import os
from pandas import DataFrame
from classes import IfcEntity
from classes.files import check_duplicates

class Ruleset:

    def __init__(self, name) -> None:
        self.name: str = name
        self.global_activity_code_type: list = [None]
        self.rules: list = []

    def display(self):

        for rule in self.rules:
            delete = rule.display()
            if delete:
                self.rules.remove(rule)
                self.save()
                st.rerun()
        
        add_rule_config = st.button('Adicionar conjunto de regras')
        if add_rule_config:
            self.rules.append(RuleConfig())
            self.save()
            st.rerun()

    def save(self):
        with open(f'./rules/{str(self.name)}.ruleset', 'wb') as file:
            pickle.dump(self, file)
        if self.name not in st.session_state['rulesets']:
            st.toast(f"{self.name} criada com sucesso", icon='🎉')
        else:
            st.toast(f"{self.name} salva com sucesso", icon='🎉')

class RuleConfig:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.rule_name: str = None
        self.rule_type = None
        self.values: list = []
        self.rule = None

    # def __repr__(self) -> str:
    #     name = self.rule_name if self.rule_name else ""
    #     return "<" + str(self.unique_id) + "-" + name + ">"

    def display(self) -> None:

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                self.rule_name = st.text_input(
                    "Nome da regra",
                    value=self.rule_name,
                    label_visibility='collapsed',
                    placeholder='Nome da regra',
                    key=f'{self.unique_id}_rule_name'
                )
            with col2:
                options = ('Filtro de elementos', 'Mapeamento de propriedade')
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
                with st.popover("Deletar", use_container_width=True):
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
            if delete_button:
                return True
            else:
                return False
    
    def rule_mapping(self):
        mapping = {
            'Filtro de elementos': ElementFilter(),
            'Mapeamento de propriedade': PropertyMapping()
        }
        if not self.rule:
            self.rule = mapping[self.rule_type]

    def delete(self):
        ruleset = pickle(open(f"./rules/{st.session_state.ruleset}.ruleset", "rb"))
        rule_config = next(x for x in ruleset.rules if x.unique_id == self.unique_id)
        ruleset.rules.remove(rule_config)
        st.rerun()

class PropertyMapping:

    def __init__(self) -> None:
        self.unique_id = uuid.uuid4()
        self.classification_items: list = None
        self.ifc_entity_type: str = None
        self.ifc_entities: list = []
        self.map_to_same_property: bool = False
        self.copy_value: bool = False
        self.origin_property: tuple = None
        self.destiny_property: tuple = None
        self.values = None

    def display(self) -> None:
        
        ifc_entity_type_options = ['IfcElement', 'IfcSpatialElement']
        attribute_options = ['Name', 'Description', 'Type', 'Material','PropertySet']

        ifc_entity = IfcEntity.ifc_entity()

        col1, col2 = st.columns([1, 4])
        with col1:
            self.ifc_entity_type = st.selectbox(
                label="Tipo da entidade IFC",
                options=ifc_entity_type_options,
                placeholder='Selecione o tipo de entidade IFC',
                index=ifc_entity_type_options.index(self.ifc_entity_type) if self.ifc_entity_type else None,
                label_visibility='collapsed',
                key=f"{self.unique_id}_ifc_entity_type_options"
            )
        if not self.ifc_entity_type:
            st.warning("Escolha entre IfcElement e IfcSpatialElement para continuar o mapeamento")
            return None
        element_options = ifc_entity.find_subclass(self.ifc_entity_type).list_all_subclasses()
        for entity in self.ifc_entities:
            if entity not in element_options:
                self.ifc_entities = None
                break
        with col2:
            self.ifc_entities = st.multiselect(
                "Selecione as IfcEntities para alterar",
                options=ifc_entity.find_subclass(self.ifc_entity_type).list_all_subclasses(),
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
            self.copy_value = st.checkbox(
                "Copiar o valor",
                value=self.copy_value,
                disabled=self.map_to_same_property,
                key=f'{self.unique_id}_map_with_same_value'
            )
        cols = st.columns(6)
        with cols[0]:
            origin_attrib = st.selectbox(
                'Atributo origem',
                attribute_options,
                index=attribute_options.index(self.origin_property[0]) if self.origin_property else None,
                key=f'{self.unique_id}_origin_attrib'
            )
        with cols[1]:
            origin_pset = st.text_input(
                'PropertySet origem',
                value=self.origin_property[1] if self.origin_property else None,
                disabled=origin_attrib != 'PropertySet',
                key=f'{self.unique_id}_origin_pset'
            )
        with cols[2]:
            origin_prop = st.text_input(
                'Property origem',
                value=self.origin_property[2] if self.origin_property else None,
                disabled=origin_attrib != 'PropertySet',
                key=f'{self.unique_id}_origin_prop'
            )
        self.origin_property = (origin_attrib, origin_pset, origin_prop)
        with cols[3]:
            destiny_attrib = st.selectbox(
                'Atributo Destino',
                attribute_options,
                index=attribute_options.index(self.destiny_property[0]) if self.destiny_property else None,
                disabled=self.map_to_same_property,
                key=f'{self.unique_id}_destiny_attrib'
            )
        with cols[4]:
            destiny_pset = st.text_input(
                'PropertySet destino',
                value=self.destiny_property[1] if self.destiny_property else None,
                disabled=destiny_attrib != 'PropertySet',
                key=f'{self.unique_id}_destiny_pset'
            )
        with cols[5]:
            destiny_prop = st.text_input(
                'Property destino',
                value=self.destiny_property[2] if self.destiny_property else None,
                disabled=destiny_attrib != 'PropertySet',
                key=f'{self.unique_id}destiny_prop'
            )
        self.destiny_property = (destiny_attrib, destiny_pset, destiny_prop)
        
        if not self.copy_value:
            df = DataFrame(self.values, columns = ['Valor modelo', 'Classificação'])
            column_config = {
                "Classificação": st.column_config.SelectboxColumn(
                    "Item da classificação",
                    options=self.classification_items,
                    required=True
                )
            }
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
        self.filter_attrs: list = [ None for _ in range(6)]
        self.values: list = []

    def display(self) -> None:

        display_dataframe = True
        attributes = ['Name', 'Description', 'Type', 'Material','PropertySet']

        cols = st.columns([1, 4])
        with cols[0]:
            n = st.number_input(
                "Escolha o número de propriedades para filtrar",
                value=len([item for item in self.filter_attrs if item]),
                min_value=0,
                max_value=6,
                step=1)
        if n == 0:
            display_dataframe = False
            self.filter_attrs = [ None for _ in range(6)]
            st.warning("Aumento o número de atributos para criar os filtros", icon='⚠️')
        if n:
            for i, col in  enumerate(st.columns(n)):
                with col:
                    if self.filter_attrs[i]:
                        value = (
                            attributes.index(self.filter_attrs[i]['Atributo']),
                            self.filter_attrs[i]['PropertySet'],
                            self.filter_attrs[i]['Property']
                        )
                    else:
                        value = (None, "", "")
                    attr = st.selectbox(
                        "Atributo",
                        index=value[0],
                        options=attributes,
                        key=f'{self.unique_id}-attr-{i}',
                        placeholder="Escolha um atributo do IFC",
                        label_visibility='collapsed'
                    )
                    pset = st.text_input(
                        'PropertySet',
                        value=value[1],
                        key=f'{self.unique_id}-pset-{i}',
                        placeholder='Escreva o nome do PropertySet',
                        label_visibility='collapsed',
                        disabled=False if attr=='PropertySet' else True
                    )
                    if attr == 'PropertySet':
                        if not pset:
                            st.warning('Necessário nome do PropertySet')
                    prop = st.text_input(
                        'PropertySet',
                        value=value[2],
                        key=f'{self.unique_id}-prop-{i}',
                        placeholder='Escreva o nome da Property',
                        label_visibility='collapsed',
                        disabled=False if attr=='PropertySet' else True
                    )
                    if attr == 'PropertySet':
                        if not prop:
                            st.warning('Necessário nome da Property')
                    filter_attr = {
                        'Atributo': attr,
                        'PropertySet': pset,
                        'Property': prop,
                        'column': attr if attr != 'PropertySet' else f'{pset}.{prop}'
                    }
                    self.filter_attrs[i] = filter_attr
        
        columns = [ filter_attr['column'] for filter_attr in self.filter_attrs if filter_attr]
        duplicates = check_duplicates(columns)
        
        if duplicates:
            display_dataframe = False
            st.error(f"Verifique se há Atributos, PropertySets e Properties duplicados. {duplicates}", icon="🚨")

        ifc_products = IfcEntity.ifc_entity().find_subclass('IfcProduct').list_all_subclasses()
        ifc_products.sort()
        operation = ['Exato', 'Contém', 'Começa com', 'Termina com']
        config = {
            'IfcEntity': st.column_config.SelectboxColumn('IfcEntity', options=ifc_products),
            'Operação': st.column_config.SelectboxColumn('Operação', options=operation),
            'Valor': st.column_config.SelectboxColumn('Valor', options=self.classification_items)
        }

        filter_attrs = [filter_attr for filter_attr in self.filter_attrs if filter_attr]
        columns = [filter_attr['column'] for filter_attr in filter_attrs if filter_attr['column']]

        if self.values:
            values = []
            for value in self.values:
                value_dict = {'IfcEntity': value['IfcEntity']}
                for column in columns:
                    if column in value:
                        value_dict.update({column: value[column]})
                    else:
                        value_dict.update({column: None})
                value_dict.update({'Valor': value['Valor']})
                values.append(value_dict)
            df = DataFrame(values)
        else:
            columns = ['IfcEntity'] + columns + ['Valor']
            df = DataFrame(columns=columns)

        if display_dataframe:
            dataframe = st.data_editor(
                data=df,
                use_container_width=True,
                column_config=config,
                num_rows='dynamic'
            )
            self.values = dataframe.to_dict(orient='records')