from surveys.core import utils
from surveys.models import *

def configure_employee_engagement():
    #INSTRUMENT:
    instrument = {
        'id': 1,
        'name': "Employee Engagement",
        'description': "An instrument that measures employee engagement"
    }

    try:
        instrument = Instrument.objects.get(id=instrument['id'])

    except Instrument.DoesNotExist as err:
        instrument = Instrument(
                id=instrument['id'],
                name=instrument['name'],
                description=instrument['description']
            )
    finally:
        instrument.name=instrument['name']
        instrument.description=instrument['description']
        instrument.save()

    #SCALE:
    scale = {
        'name':"How often? Scale of One to Five",
        'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
        'opt_out'True:,
        'min_value':1,
        'max_value':5,
        'min_value_description':"never",
        'max_value_description':"always",
    }

    try:
        scale = Scale.objects.get(
            name=scale['name'],
            instruction=scale['instruction'],
            opt_out=scale['opt_out'],
            min_value=scale['min_value'],
            max_value=scale['max_value'],
            min_value_description=scale['min_value_description'],
            max_value_description=scale['max_value_description']
        )
    except Scale.DoesNotExist as err:
        #make a new attached Scale
        scale = Scale(
            name=scale['name'],
            instruction=scale['instruction'],
            opt_out=scale['opt_out'],
            min_value=scale['min_value'],
            max_value=scale['max_value'],
            min_value_description=scale['min_value_description'],
            max_value_description=scale['max_value_description']
        )
    finally:
        pass #Scale objects cannot be changed


    #Dimensions
    vigor = {
        'instrument': instrument,
        'name': "Vigor",
        'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        'scale': scale
    }

    dedication = {
        'instrument': instrument,
        'name': "Dedication",
        'description': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
        'scale': scale
    }
    absorption = {
        'instrument': instrument,
        'name': "Absorption",
        'description': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
        'scale': scale
    }
    raw_dimensions = [vigor, dedication, absorption]

    #ensure there are no unwanted dimensions for the instrument:
    current_dimensions = instrument.dimension_set.all()
    if len(current_dimensions)>0:
        r_names = [rd['name'] for rd in raw_dimensions]
        for d in current_dimensions:
            if d.name not in r_names:
                d.instrument=None
                d.save()

    for d in raw_dimensions:
        try:
            existing_d = Dimension.object.get(
                instrument=d['instrument'],
                name=d['name'],
            )
            if existing_d.description != d['description']:
                existing_d.description = d['description']
                existing_d.save()
            if d['scale'] != existing_d.scale:
                existing_d.instrument=None
                existing_d.save()
                raise ValueError('The saved Scale for the %s-Dimension is different from the one in the product configuration (%s != %s).'%(existing_d.name,  existing_d.scale, d['scale']))

        except Dimensions.DoesNotExist, ValueError:
            new_d = Dimension(
                instrument=d['instrument'],
                named=d['name'],
                description=d['description'],
                scale=d['scale']
            )
            new_d.save()

    dimensions = Dimension.objects.filter(instrument=instrument)
    assert len(dimensions) == len(raw_dimensions), "Somehow we have ended up with %s dimensions for %s-instrument, while trying to have %s."%(len(dimensions), instrument.name, len(raw_dimensions))

    #Items
    i001 = {
        'dimension': dimensions[0],
        'formulation' :,
        'active' :,
        'inverted' :,
    }
