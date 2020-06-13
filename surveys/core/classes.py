
class Instrument:
    '''
    An Instrument is blueprint for a Survey (a Model for a single point in time
    survey sent to a customer's employees).
    '''
    def __init__(self, name, description, dimension_list):
        #Check that proper input has been given
        assert isinstance(name, str), 'The name of the Instrument object must be a string, got %s.'%(type(name))
        assert isinstance(description, str), 'The description of the Instrument object must be a string, got %s.'%(type(descrition))
        for dimension in dimension_list:
            assert isinstance(dimension, Dimension), 'All dimensions in the dimension_list provided for a new Instrument must be Dimension instances, but was %s'%(type(dimension))

        #Initiale properties
        self.name = name
        self.description = description
        self.dimension_list = dimension_list

    def __str__(self):
        return self.name

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.name)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def get_items(self):
        items = []
        for d in self.dimension_list:
            for i in d.item_list:
                i.dimension = d
                items.append(i)
        return items

class Dimension:
    def __init__(self, name, description, item_list):
        #Check that proper input has been given
        assert isinstance(name, str), 'The name of the Dimension object must be a string, got %s.'%(type(name))
        assert isinstance(description, str), 'The description of the Dimension object must be a string, got %s.'%(type(descrition))
        for item in item_list:
            assert isinstance(item, Item), 'All items in the item_list provided for a new Dimension must be Item instances, but was %s'%(type(item))

        #Initiate properties
        self.name = name
        self.description = description
        self.item_list = item_list

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.name)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def __str__(self):
        return self.name


class Item:
    def __init__(self, formulation, instruction_string='', active=True, options=[1, 2, 3, 4, 5], inverted=False):
        #Check that proper input has been given
        assert isinstance(formulation, str), 'The formulation of the Item object must be a string, got %s.'%(type(formulation))
        assert isinstance(instruction_string, str), 'The instruction_string of the Item object must be a string, got %s.'%(type(instruction_string))
        assert isinstance(active, bool), 'The active argument for new Items must me a bool, but was %s'%(type(active))
        assert isinstance(options, list), 'The options argument for new Items must me a list of values, but was %s'%(type(options))

        #Initiale properties
        self.formulation = formulation
        self.active = active
        self.instruction_string = instruction_string
        self.options = options

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.formulation)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def __str__(self):
        return self.formulation
