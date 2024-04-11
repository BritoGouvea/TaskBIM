class IfcEntity:

    @staticmethod
    def ifc_entity():
        tuples = []
        with open('./assets/ifc.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                level = int(line.count('•')/2) + 1
                entity = line.replace('•','')
                pair = (level, entity[:-1])
                tuples.append(pair)
        ifc_entity = IfcEntity(0, 'IfcEntity', None, tuples)
        ifc_entity.subclasses_from_substack()
        return ifc_entity

    def __init__(self, level, name, base_class, substack) -> None:
        self.level = level
        self.name = name
        self.base_class = base_class
        self.subclasses = []
        self.substack = substack
    
    def __repr__(self) -> str:
        return f"<{self.name}>"

    def subclasses_from_substack(self):
        for t in self.substack:
            if t[0] == self.level + 1:
                actual_base = IfcEntity(t[0], t[1], self, [])
                self.subclasses.append(actual_base)
            else:
                actual_base.substack.append(t)
        for entity in self.subclasses:
            entity.subclasses_from_substack()

    def find_subclass(self, subclass_name: str):
        if self.name == subclass_name:
            return self
        for subclass in self.subclasses:
            result = subclass.find_subclass(subclass_name)
            if result:
                return result
    
    def list_all_subclasses(self, subclasses_names: list = None) -> list:
        if not subclasses_names:
            subclasses_names = []
        for subclass in self.subclasses:
            subclasses_names.append(subclass.name)
            subclass.list_all_subclasses(subclasses_names)
        return subclasses_names