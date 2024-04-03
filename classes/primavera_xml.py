import xml.etree.ElementTree as ET

# Functions
        
def read_plan(xml_file):
    tree = ET.parse(xml_file)
    for element in tree.iter():
        element.tag = element.tag.split("}")[-1]
    return tree.getroot()

def get_subelement(element, tag: str):
    return [ subelement for subelement in element.findall(tag)]

def get_values(element, tags: list):
    _all = {'element': element}
    return _all | { tag: element.find(tag).text for tag in tags}

# Classes

class Plan:

    def __init__(self, xml_file_path: str) -> None:
        self.root = read_plan(xml_file_path)
        self.ActivityCodeTypes = ActivityCodeType.get_all(self.root)
        self.ActivityCodes = ActivityCode.get_all(self.root, self.ActivityCodeTypes)
        self.Project = get_subelement(self.root, 'Project')[0]
        self.Activities = Activity.get_all(self.Project, self.ActivityCodeTypes, self.ActivityCodes)

class ActivityCodeType:

    @staticmethod
    def get_all(root):
        elements = get_subelement(root, 'ActivityCodeType')
        project = get_subelement(root, 'Project')[0]
        elements.extend(get_subelement(project, 'ActivityCodeType'))
        elements = [get_values(element, ['ObjectId', 'Name']) for element in elements]
        return { element['ObjectId']: ActivityCodeType(element) for element in elements } 

    def __init__(self, element):
        self.ObjectId = element['ObjectId']
        self.Name = element['Name']
        self.ActivityCodes = []

    def __repr__(self):
        return f"{self.Name}"

class ActivityCode:

    @staticmethod
    def get_all(root, activity_code_types):
        elements = get_subelement(root, 'ActivityCode')
        project = get_subelement(root, 'Project')[0]
        elements.extend(get_subelement(project, 'ActivityCode'))
        elements = [get_values(element, ['CodeTypeObjectId', 'ObjectId', 'Description']) for element in elements]
        return { element['ObjectId']: ActivityCode(element, activity_code_types) for element in elements }

    def __init__(self, element, activity_code_types):
        self.CodeTypeObject = activity_code_types[element['CodeTypeObjectId']]
        self.CodeTypeObject.ActivityCodes.append(self)
        self.ObjectId = element['ObjectId']
        self.Description = element['Description']

    def __repr__(self) -> str:
        return f"{self.CodeTypeObject.ObjectId} - {self.CodeTypeObject.Name}, {self.Description}"

class Activity:

    @staticmethod
    def get_all(project, code_types, codes):
        elements = get_subelement(project, 'Activity')
        return [Activity(element, codes) for element in elements]

    def __init__(self, element, codes) -> None:
        values = get_values(element, ['Id', 'Name', 'ObjectId'])
        self.Id = values['Id']
        self.Name = values['Name']
        self.ObjectId = values['ObjectId']
        self.ActivityCodes = {
                item.CodeTypeObject.Name: item.Description
                for item in [codes[code.find('ValueObjectId').text] for code in get_subelement(element, 'Code')]
            }
    
    def __repr__(self) -> str:
        return f"{self.Id} - {self.Name}"