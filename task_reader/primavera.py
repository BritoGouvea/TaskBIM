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

    def __init__(self, xml_file: str) -> None:
        self.root = read_plan(xml_file)
        self.ActivityCodeTypes = ActivityCodeType.get_all(self.root)
        self.ActivityCodes = ActivityCode.get_all(self.root, self.ActivityCodeTypes)
        self.project = Project(get_subelement(self.root, 'Project')[0], self.ActivityCodeTypes, self.ActivityCodes)

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

class Project:

    def __init__(self, element, code_types, codes):
        self.Name = element.find('Name').text
        self.Wbs = Wbs.get_all(element)
        self.Activities = Activity.get_all(element, code_types, codes)

    def __repr__(self) -> str:
        return f"self.Name"

class Wbs:

    @staticmethod
    def get_all(project):
        elements = get_subelement(project, 'WBS')
        elements = [get_values(element, ['ObjectId', 'Code', 'Name', 'ParentObjectId']) for element in elements]
        return { element['ObjectId']: Wbs(element) for element in elements }


    def __init__(self, element):
        self.ObjectId = element['ObjectId']
        self.Code = element['Code']
        self.Name = element['Name']
        self.ParentObject = element['ParentObjectId']
        self.Children = []
        self.Activities = []

class Activity:

    @staticmethod
    def get_all(project, code_types, codes):
        elements = get_subelement(project, 'Activity')
        elements = [get_values(element, ['Id', 'Name', 'ObjectId', 'WBSObjectId']) for element in elements]
        return { element['ObjectId']: Activity(element, code_types, codes) for element in elements }

    def __init__(self, element, code_types, codes) -> None:
        self.Id = element['Id']
        self.Name = element['Name']
        self.ObjectId = element['ObjectId']
        _codes = [ get_values(Code, ['TypeObjectId', 'ValueObjectId'] ) for Code in element['element'].findall('Code') ]
        __codes = { code_types[_code['TypeObjectId']].Name: codes[_code['ValueObjectId']] for _code in _codes }
        self.Codes = __codes
        # self.WBSObject = wbs[element['WBSObjectId']]
    
    # def __repr__(self) -> str:
    #     return f"{self.Id} - {self.Name}"


