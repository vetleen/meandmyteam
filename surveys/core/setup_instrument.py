from surveys.models import *

def setup_instrument(raw_instrument):
    #assertions

    #assert that we have all four pieces
    assert 'instrument' in raw_instrument, "setup_instrument was called without 'instrument' in raw_instrument"
    assert 'scales' in raw_instrument, "setup_instrument was called without 'scales' in raw_instrument"
    assert 'dimensions' in raw_instrument, "setup_instrument was called without 'dimensions' in raw_instrument"
    assert 'items' in raw_instrument, "setup_instrument was called without 'items' in raw_instrument"

    #assert types are correct
    assert type(raw_instrument['instrument']) == dict, "raw_instrument['instrument'] was type %s, expected dict"%(type(raw_instrument['instrument']))
    assert type(raw_instrument['scales']) == list, "raw_instrument['scales'] was type %s, expected list"%(type(raw_instrument['scales']))
    assert type(raw_instrument['dimensions']) == list, "raw_instrument['dimensions'] was type %s, expected list"%(type(raw_instrument['dimensions']))
    assert type(raw_instrument['items']) == list, "raw_instrument['items'] was type %s, expected list"%(type(raw_instrument['items']))

    ##... inside instrument
    assert type(raw_instrument['instrument']['id']) == int, "raw_instrument['instrument']['id'] was type %s, expected int"%(type(raw_instrument['instrument']['id']))
    assert type(raw_instrument['instrument']['name']) == str, "raw_instrument['instrument']['name'] was type %s, expected str"%(type(raw_instrument['instrument']['name']))
    assert type(raw_instrument['instrument']['description']) == str, "raw_instrument['instrument']['description'] was type %s, expected str"%(type(raw_instrument['instrument']['description']))

    ##... inside scales
    for n, s in enumerate(raw_instrument['scales']):
        assert type(s) == dict, "raw_instrument['scales'][%s] was type %s, expected dict"%(n, type(s))
        assert type(s['type']) == str, "raw_instrument['scales'][%s]['type'] was type %s, expected str"%(n, type(s['type']))
        assert type(s['name']) == str, "raw_instrument['scales'][%s]['name'] was type %s, expected str"%(n, type(s['name']))
        assert type(s['instruction']) == str, "raw_instrument['scales'][%s]['instruction'] was type %s, expected str"%(n, type(s['instruction']))
        assert type(s['opt_out']) == bool, "raw_instrument['scales'][%s]['opt_out'] was type %s, expected bools"%(n, type(s['opt_out']))
        assert type(s['min_value']) == int, "raw_instrument['scales'][%s]['min_value'] was type %s, expected int"%(n, type(s['min_value']))
        assert type(s['max_value']) == int, "raw_instrument['scales'][%s]['max_value'] was type %s, expected int"%(n, type(s['max_value']))
        assert type(s['min_value_description']) == str, "raw_instrument['scales'][%s]['min_value_description'] was type %s, expected str"%(n, type(s['min_value_description']))
        assert type(s['max_value_description']) == str, "raw_instrument['scales'][%s]['max_value_description'] was type %s, expected str"%(n, type(s['max_value_description']))

    ##... inside dimensions
    for n, d in enumerate(raw_instrument['dimensions']):
        assert type(d) == dict, "raw_instrument['dimensions'][%s] was type %s, expected dict"%(n, type(d))
        assert type(d['instrument_id']) == int, "raw_instrument['dimensions'][%s][instrument_id'] was type %s, expected int"%(n, type(d['instrument_id']))
        assert type(d['name']) == str, "raw_instrument['dimensions'][%s]['name'] was type %s, expected str"%(n, type(d['name']))
        assert type(d['description']) == str, "raw_instrument['dimensions'][%s]['description'] was type %s, expected str"%(n, type(d['description']))
        assert type(d['scale_location']) == int, "raw_instrument['dimensions'][%s][scale_location'] was type %s, expected int"%(n, type(d['scale_location']))

    ##... inside items
    for n, i in enumerate(raw_instrument['items']):
        assert type(i) == dict, "raw_instrument['items'][%s] was type %s, expected dict"%(n, type(i))
        assert type(i['dimension_location']) == int, "raw_instrument['dimensions'][%s]['dimension_location'] was type %s, expected int"%(n, type(d['dimension_location']))
        assert type(i['formulation']) == str, "raw_instrument['dimensions'][%s]['formulation'] was type %s, expected str"%(n, type(d['formulation']))
        assert type(i['active']) == bool, "raw_instrument['dimensions'][%s]['active'] was type %s, expected bool"%(n, type(d['active']))
        assert type(i['inverted']) == bool, "raw_instrument['dimensions'][%s]['inverted'] was type %s, expected bool"%(n, type(d['inverted']))

    #assert that the the index for desired Scale to be found in scales-list is valid
    for d in raw_instrument['dimensions']:
        assert d['scale_location'] < len(raw_instrument['scales']), "Please make sure dimensions are provided with the proper scales-indexes (you proved %s as the index, but there were only %s items."%(d['scale_location'], len(raw_instrument['scales']))#if there are 3 items, len is 3 and the max index allowed is 2

    #assert that the instrument provided with each dimensions is the same as the instrument supplied
    for d in raw_instrument['dimensions']:
        assert raw_instrument['instrument']['id'] == d['instrument_id'], "Please make sure all dimensions' ['instrument_id'] is the same as the ['instrument']['id']"

    #We seemingly have valid inputs, now let's make sure the product is set up properly:
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
    #print("Reached Scales, working with:")
    #print(raw_instrument['scales'])
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
    #print("Finished Scales, now working with:")
    #for s in scales:
    #    print("Scale: ", s.name)

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
    #print("Reached Dimensions, now working with:")
    #for d in raw_instrument['dimensions']:
    #    print("Scale: ", d['scale'].name)
    for d in raw_instrument['dimensions']:
        #print("Looking at dimensions")
        try:
            #print("Trying to find existing")
            existing_d = Dimension.objects.get(
                instrument=d['instrument'],
                name=d['name']
            )
            #print("Found existing")
            if existing_d.description != d['description']:
                #If there's a new description, we can change that
                #print("Needs new description")
                existing_d.description = d['description']
                existing_d.save()
            if d['scale'] != existing_d.scale:
                #If there's a new scale, scrap the dimension, and make a new one
                #print("Needs scraping and to make a new one!")
                existing_d.instrument=None
                existing_d.save()
                new_d = Dimension(
                    instrument=d['instrument'],
                    name=d['name'],
                    description=d['description'],
                    scale=d['scale']
                )
                new_d.save()
                #print("Should have anew one!")

        except Dimension.DoesNotExist:
            new_d = Dimension(
                instrument=d['instrument'],
                name=d['name'],
                description=d['description'],
                scale=d['scale']
            )
            new_d.save()

    dimensions = Dimension.objects.filter(instrument=instrument)
    #print("Have these scales:")
    #for d in dimensions:
    #    print(d.scale.name)
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
                i.delete()
    items = instrument.get_items()
    assert len(items) == len(raw_instrument['items']), "Somehow we have ended up with %s items for %s-instrument, while trying to have %s."%(len(items), instrument.name, len(raw_instrument['items']))
