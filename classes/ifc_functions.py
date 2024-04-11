import json
from ifc_classification import open_ifc_in_memory
import ifcopenshell
import ifcopenshell.util.element as IfcElement
from classes.rules import PropertyMapping
import re
from itertools import chain

def check_ifc_element(ifc_element, filtro):

    def check_value(value, filtro):
        if filtro['Operação'] == 'Exato':
            return value == filtro['Valor']
        if filtro['Operação'] == 'Contém':
            return filtro['Valor'] in value
        if filtro['Operação'] == 'Começa com':
            return value.startswith(filtro['Valor'])
        if filtro['Operação'] == 'Termina com':
            return value.endswith(filtro['Valor'])

    if filtro['Propriedade'] == 'Name':
        return check_value(ifc_element.Name, filtro)
    if filtro['Propriedade'] == 'Description':
        return check_value(ifc_element.Description, filtro)
    if filtro['Propriedade'] == 'Type':
        TypeName = ifc_element.ObjectType
        if not TypeName:
            TypeName = IfcElement.get_type(ifc_element).Name
        return check_value(TypeName, filtro)
    if filtro['Propriedade'] == 'Material':
        Material = IfcElement.get_material(ifc_element)
        return check_value(Material, filtro)
    if filtro['Propriedade'] == 'PropertySet':
        Property = IfcElement.get_pset(ifc_element, filtro['PropertySet'], filtro['Property'])
        return check_value(Property, filtro)
    return False

def get_elements_by_filter(ifc_file: ifcopenshell.file, rules: dict):

    classification_name = list(rules.keys())[0]
    filtros = rules[classification_name]
    filtered_ifc_elements = []
    for filtro in filtros:
        ifc_elements = ifc_file.by_type(filtro['Component']) if filtro['Component'] else ifc_file.by_type('IfcElement')
        for f in filtro['Dataframe']:
            filtered_ifc_elements.extend([ ifc_element for ifc_element in ifc_elements if check_ifc_element(ifc_element, f) ])
    return {'ClassificationName': classification_name, 'IfcElements': filtered_ifc_elements}

def pep_filter(ifc_file, regras):
    
    regras = [ {key: regra} for key, regra in regras['PEP'].items() if regra ]
    return [(get_elements_by_filter(ifc_file, regra)) for regra in regras]

def create_pep_classification(ifc_file, pep_elements):

    ifc_classification = ifc_file.create_entity('IfcClassification',
                                               'Tegra',
                                               '1.0',
                                               None,
                                               'PEP')
    for pep_element in pep_elements:
        classify_ifc(ifc_file, pep_element, ifc_classification)

def classify_ifc(ifc_file, elements_list, ReferenceSource):
    
    Location = 'Tegra'
    ItemReference, Name = elements_list['ClassificationName'].split("* - ")
    classification_reference = ifc_file.create_entity('IfcClassificationReference',
                                                  Location,
                                                  ItemReference,
                                                  Name,
                                                  ReferenceSource)
    ifc_file.create_entity('IfcRelAssociatesClassification',
                            ifcopenshell.guid.new(),
                            ifc_file.by_type('IfcOwnerHistory')[0],
                            None,
                            None,
                            elements_list['IfcElements'],
                            classification_reference
                            )

def process_classification(ifc_file):

    ifc_model = open_ifc_in_memory(ifc_file)
    regras = json.load(open('./assets/regras.json'))
    elements_list = pep_filter(ifc_model, regras)
    create_pep_classification(ifc_model, elements_list)
    return ifc_model


def check_wildcard_match(value, pattern):
    if "*" not in pattern:
        return value == pattern
    # Convert pattern to a regular expression with wildcards replaced by appropriate symbols
    pattern_regex = re.sub(r"\*", ".*", pattern)
    # Perform a regular expression match
    match = re.search(pattern_regex, value)
    # Return True if there's a match, False otherwise
    return match is not None

def get_element_attribute(ifc_element, attribute):

    get_attributes = {
        "Name": lambda e: e.Name,
        "Description": lambda e: e.Description,
        "Type": lambda e: e.ObjectType or IfcElement.get_type(e),
        "Material": lambda e: IfcElement.get_material(e),
        "PropertySet": lambda e: IfcElement.get_pset(e, attribute[1], attribute[2])
    }
    return get_attributes[attribute[0]](ifc_element)

def check_value(ifc_element, attribute, pattern):

    attr = get_element_attribute(ifc_element, attribute)
    return (check_wildcard_match(attr, pattern))

def set_ifc_attribute(values: dict, attribute):

    set_mapping = {
        "Name": lambda e, v: setattr(e, 'Name', v),
        "Description": lambda e, v: setattr(e, 'Description', v),
        "Type": lambda e, v: setattr(e, 'ObjectType', v),
        "Material": lambda e: IfcElement.get_material(e),
        "PropertySet": lambda e: IfcElement.get_pset(e, attribute[1], attribute[2])
    }
    for set_value, elements in values.items():
        for element in elements:
            set_mapping[attribute[0]](element, set_value)

def property_mapping(ifc_model: ifcopenshell.ifcopenshell.file, rule: PropertyMapping):

    # Valida se o parâmetro de entrada está dentro do padrão
    classification_dict = {}

    ifc_entities = [
        item for generator in (ifc_model.by_type(ifc_entity) for ifc_entity in rule.ifc_entities)
        for item in generator
    ]

    for value in rule.values:
        valid_entities = [ifc_entity for ifc_entity in ifc_entities
                            if check_value(ifc_entity, rule.origin_property, value['Valor modelo'])]
        if value['Classificação'] not in classification_dict:
            classification_dict.update({value['Classificação']: valid_entities})
        else:
            classification_dict[value['Classificação']].append(valid_entities)
    if rule.map_to_same_property:
        destiny_attr = rule.origin_property
    else:
        destiny_attr = rule.destiny_property
    set_ifc_attribute(classification_dict, destiny_attr)
    
    return ifc_entities

if __name__ == '__main__':
    
    process_classification()