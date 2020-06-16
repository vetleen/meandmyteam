from surveys.models import *

def setup_instrument(raw_instrument):
    #assertions

    #assert that the instrument provided with each dimensions is the same as the instrument supplied
    for d in raw_instrument['dimensions']:
        assert raw_instrument['instrument']['id'] == d['instrument_id'], "Make sure all dimensions' ['instrument_id'] is the same as the ['instrument']['id']"

    ###############
    #INSTRUMENT:
    try:
        instrument = Instrument.objects.get(id=raw_instrument['instrument']['id'])
        instrument.name=raw_instrument['instrument']['name']
        instrument.description=raw_instrument['instrument']['description']

    except Instrument.DoesNotExist as err:
        instrument = Instrument(
                id=raw_instrument['instrument']['id'],
                name=raw_instrument['instrument']['name'],
                description=raw_instrument['instrument']['description']
            )

    finally:
        instrument.save()

    ############
    #SCALE:
    scales=[]
    for scale in raw_instrument['scales']:
        if scale['type'] == "RatioScale":
            try:
                scale = RatioScale.objects.get(
                    name=scale['name'],
                    instruction=scale['instruction'],
                    opt_out=scale['opt_out'],
                    min_value=scale['min_value'],
                    max_value=scale['max_value'],
                    min_value_description=scale['min_value_description'],
                    max_value_description=scale['max_value_description']
                )

            except RatioScale.DoesNotExist as err:
                #make a new attached Scale
                scale = RatioScale(
                    name=scale['name'],
                    instruction=scale['instruction'],
                    opt_out=scale['opt_out'],
                    min_value=scale['min_value'],
                    max_value=scale['max_value'],
                    min_value_description=scale['min_value_description'],
                    max_value_description=scale['max_value_description']
                )
                scale.save()

            finally:
                scales.append(scale)

        else:
            raise ValueError("scale['%s'] provided, but not supported. Try 'RatioScale'."%(scale['type']))
    assert len(scales) == len(raw_instrument['scales'])


    ################
    #DIMENSIONS

    #add actual Instrument and Scale objects to raw_data
    for d in raw_instrument['dimensions']:
        #print(type(d['instrument']))
        #print(d['instrument'])
        real_inst = Instrument.objects.get(id=d['instrument_id'])
        real_scale = scales[d['scale_location']]
        d['instrument'] = real_inst
        d['scale'] = real_scale

    #ensure there are no unwanted dimensions for the instrument:
    current_dimensions = instrument.dimension_set.all()
    if len(current_dimensions)>0:
        raw_names = [d['name'] for d in raw_instrument['dimensions']]
        for d in current_dimensions:
            if d.name not in raw_names:
                d.instrument=None
                d.save()

    #Ensure wanted dimesnions are found:
    for d in raw_instrument['dimensions']:
        try:
            existing_d = Dimension.objects.get(
                instrument=d['instrument'],
                name=d['name']
            )
            if existing_d.description != d['description']:
                existing_d.description = d['description']
                existing_d.save()
            if d['scale'] != existing_d.scale:
                existing_d.instrument=None
                existing_d.save()
                new_d = Dimension(
                    instrument=d['instrument'],
                    named=d['name'],
                    description=d['description'],
                    scale=d['scale']
                )
                new_d.save()

        except Dimension.DoesNotExist:
            new_d = Dimension(
                instrument=d['instrument'],
                name=d['name'],
                description=d['description'],
                scale=d['scale']
            )
            new_d.save()

    dimensions = Dimension.objects.filter(instrument=instrument)
    assert len(dimensions) == len(raw_instrument['dimensions']), "Somehow we have ended up with %s dimensions for %s-instrument, while trying to have %s."%(len(dimensions), instrument.name, len(raw_instrument['dimensions']))

    ######
    #ITEMS
    #add dimension paramter to items from dimension_location

    for i in raw_instrument['items']:
        real_dimension = dimensions[i['dimension_location']]
        i.update({'dimension': real_dimension})

    #make a list with DB Item objects for all Items in raw_items
    items=[]
    for ritem in raw_instrument['items']:
        real_dimension = dimensions[ritem['dimension_location']]

        try:
            i = Item.objects.get(
                dimension=ritem['dimension'],
                formulation=ritem['formulation'],
                active=ritem['active'],
                inverted=ritem['inverted']
            )
        except Item.DoesNotExist:
            i = Item(
                dimension=ritem['dimension'],
                formulation=ritem['formulation'],
                active=ritem['active'],
                inverted=ritem['inverted']
            )
            i.save()

        finally:
            items.append(i)

    #Make sure there are no extra Items claiming to beloing to our dimensions (let's say a change was made, the old Item will stil be here)
    all_items = instrument.get_items()

    if len(all_items) != len(raw_instrument['items']):
        for i in all_items:
            if i not in items:
                i.dimension=None
                i.save()
                i.delete()
    items = instrument.get_items()
    assert len(items) == len(raw_instrument['items']), "Somehow we have ended up with %s items for %s-instrument, while trying to have %s."%(len(items), instrument.name, len(raw_instrument['items']))
