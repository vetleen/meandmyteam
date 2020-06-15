from surveys.models import *

def create_instrument(id, name, description=None):
    i = Instrument(
            id=id,
            name = name,
            description = description,
        )
    i.save()
    return i

def create_ratio_scale(name, instruction=None, opt_out=True, min_value=0, max_value=0, min_value_description=None, max_value_description=None):
    rs = RatioScale(
            name=name,
            instruction=instruction,
            opt_out=opt_out,
            min_value=min_value,
            max_value=max_value,
            min_value_description=min_value_description,
            max_value_description=max_value_description
        )
    rs.save()
    return rs

def create_dimension(instrument, name, scale, description=None):
    d=Dimension(
            instrument=instrument,
            name=name,
            description=description,
            scale=scale
        )
    d.save()
    return d

def create_item(dimension, formulation, active=True, inverted=False):
    i = Item(
            dimension = dimension,
            formulation = formulation,
            active = active,
            inverted = inverted
        )
    i.save()
    return i

def create_or_retrieve_product(instrument, scale, dimension, item):
    #Make or retreive Instrument
    try:
        instrument = Instrument.objects.get(id=1)
    except Instrument.DoesNotExist as err:
        instrument = util.create_instrument(name=desired_name)
