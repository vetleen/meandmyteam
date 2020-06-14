
'''
THESE ARE THE CLASSES THAT ARE NEEDED TO MAKE THE PRODUCTS THAT CUSTOMERS CAN
OPT IN TO:

Instrument
The Instrument class represents the product, and has a list of dimensions that
we are insterested in measuring

Dimension
The Dimension class represents a theoretical dimension that we are interested in
measuring, and has a list of items that measure that dimension. It also has a
Scale connected with it, that represents the options items measuring this
dimension will have.

Item
The concrete questions or statements that Respondents will have to score.

Scale
The options that a item has for scoring.

'''

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
    def __init__(self, name, description, item_list, scale=None):
        #Check that proper input has been given
        assert isinstance(name, str), 'The name of the Dimension object must be a string, got %s.'%(type(name))
        assert isinstance(description, str), 'The description of the Dimension object must be a string, got %s.'%(type(descrition))
        for item in item_list:
            assert isinstance(item, Item), 'All items in the item_list provided for a new Dimension must be Item instances, but was %s'%(type(item))

        #Initiate properties
        self.name = name
        self.description = description
        self.item_list = item_list
        self.scale = scale

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.name)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def __str__(self):
        return self.name


class Item:
    def __init__(self, formulation, instruction_string='', active=True, inverted=False):
        #Check that proper input has been given
        assert isinstance(formulation, str), 'The formulation of the Item object must be a string, got %s.'%(type(formulation))
        assert isinstance(active, bool), 'The active argument for new Items must me a bool, but was %s'%(type(active))
        assert isinstance(inverted, bool), 'The inverted argument for new Items must me a bool, but was %s'%(type(active))

        #Initiale properties
        self.formulation = formulation
        self.active = active
        self.inverted = inverted

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.formulation)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def __str__(self):
        return self.formulation

class Scale:
    def __init__(self, name, instruction_string, opt_out=True):
        #Check that proper input has been given
        assert isinstance(name, str), 'The name of the Scale object must be a string, got %s.'%(type(formulation))
        assert isinstance(instruction_string, str), 'The instruction_string of the Item object must be a string, got %s.'%(type(instruction_string))

        assert isinstance(opt_out, bool), 'The opt_out argument for Scales must me a bool, but was %s'%(type(active))

        #Initiale properties
        self.opt_out = opt_out
        self.name = name
        self.instruction_string = instruction_string

    def __repr__(self):
        whatami = str(type(self))
        whoami = str(self.name)
        rep_string =  whatami + ': ' + whoami
        return rep_string

    def __str__(self):
        return self.name

class RatioScale(Scale):
    def __init__(
            self,
            name,
            instruction_string,
            opt_out=True,
            min_value=0,
            max_value=10,
            min_value_description=None,
            max_value_description=None
        ):

        #Check that proper input has been given
        assert isinstance(min_value, int), 'The min_value of the Scale object must be an int, got %s.'%(type(formulation))
        assert isinstance(max_value, int), 'The max_value of the Scale object must be an int, got %s.'%(type(formulation))
        if min_value_description is not None:
            assert isinstance(name, str), 'The min_value_description of the Scale object must be a string, got %s.'%(type(formulation))
        if max_value_description is not None:
            assert isinstance(name, str), 'The max_value_description of the Scale object must be a string, got %s.'%(type(formulation))

        #Initiale properties
        self.min_value = min_value
        self.max_value = max_value
        self.min_value_description = min_value_description #e.g. "Disagree completely"
        self.max_value_description = max_value_description #e.g. "Agree completly"
        super().__init__(name=name, instruction_string=instruction_string, opt_out=opt_out)
