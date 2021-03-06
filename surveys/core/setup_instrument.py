from surveys.models import *

#set up logging
import datetime
import logging
logger = logging.getLogger('__name__')

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
    assert type(raw_instrument['instrument']['slug_name']) == str, "raw_instrument['instrument']['slug_name'] was type %s, expected str"%(type(raw_instrument['instrument']['slug_name']))
    assert type(raw_instrument['instrument']['description']) == str, "raw_instrument['instrument']['description'] was type %s, expected str"%(type(raw_instrument['instrument']['description']))
    assert type(raw_instrument['instrument']['name_nb']) == str, "raw_instrument['instrument']['name_nb'] was type %s, expected str"%(type(raw_instrument['instrument']['name_nb']))
    assert type(raw_instrument['instrument']['slug_name_nb']) == str, "raw_instrument['instrument']['slug_name_nb'] was type %s, expected str"%(type(raw_instrument['instrument']['slug_name_nb']))
    assert type(raw_instrument['instrument']['description_nb']) == str, "raw_instrument['instrument']['description_nb'] was type %s, expected str"%(type(raw_instrument['instrument']['description_nb']))
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
        assert type(s['instruction_nb']) == str, "raw_instrument['scales'][%s]['instruction_nb'] was type %s, expected str"%(n, type(s['instruction_nb']))
        assert type(s['min_value_description_nb']) == str, "raw_instrument['scales'][%s]['min_value_description_nb'] was type %s, expected str"%(n, type(s['min_value_description_nb']))
        assert type(s['max_value_description_nb']) == str, "raw_instrument['scales'][%s]['max_value_description_nb'] was type %s, expected str"%(n, type(s['max_value_description_nb']))
    ##... inside dimensions
    for n, d in enumerate(raw_instrument['dimensions']):
        assert type(d) == dict, "raw_instrument['dimensions'][%s] was type %s, expected dict"%(n, type(d))
        assert type(d['instrument_id']) == int, "raw_instrument['dimensions'][%s][instrument_id'] was type %s, expected int"%(n, type(d['instrument_id']))
        assert type(d['name']) == str, "raw_instrument['dimensions'][%s]['name'] was type %s, expected str"%(n, type(d['name']))
        assert type(d['description']) == str, "raw_instrument['dimensions'][%s]['description'] was type %s, expected str"%(n, type(d['description']))
        assert type(d['scale_location']) == int, "raw_instrument['dimensions'][%s][scale_location'] was type %s, expected int"%(n, type(d['scale_location']))
        assert type(d['name_nb']) == str, "raw_instrument['dimensions'][%s]['name_nb'] was type %s, expected str"%(n, type(d['name_nb']))
        assert type(d['description_nb']) == str, "raw_instrument['dimensions'][%s]['description_nb'] was type %s, expected str"%(n, type(d['description_nb']))
    ##... inside items
    for n, i in enumerate(raw_instrument['items']):
        assert type(i) == dict, "raw_instrument['items'][%s] was type %s, expected dict"%(n, type(i))
        assert type(i['dimension_location']) == int, "raw_instrument['dimensions'][%s]['dimension_location'] was type %s, expected int"%(n, type(d['dimension_location']))
        assert type(i['formulation']) == str, "raw_instrument['dimensions'][%s]['formulation'] was type %s, expected str"%(n, type(d['formulation']))
        assert type(i['active']) == bool, "raw_instrument['dimensions'][%s]['active'] was type %s, expected bool"%(n, type(d['active']))
        assert type(i['inverted']) == bool, "raw_instrument['dimensions'][%s]['inverted'] was type %s, expected bool"%(n, type(d['inverted']))
        assert type(i['formulation_nb']) == str, "raw_instrument['dimensions'][%s]['formulation_nb'] was type %s, expected str"%(n, type(d['formulation_nb']))

    #assert that the the index for desired Scale to be found in scales-list is valid
    for d in raw_instrument['dimensions']:
        assert d['scale_location'] < len(raw_instrument['scales']), "Please make sure dimensions are provided with the proper scales-indexes (you proved %s as the index, but there were only %s items."%(d['scale_location'], len(raw_instrument['scales']))#if there are 3 items, len is 3 and the max index allowed is 2

    #assert that the instrument provided with each dimensions is the same as the instrument supplied
    for d in raw_instrument['dimensions']:
        assert raw_instrument['instrument']['id'] == d['instrument_id'], "Please make sure all dimensions' ['instrument_id'] is the same as the ['instrument']['id']"

    logger.warning("... ... ... passed all assertions.")

    #We seemingly have valid inputs, now let's make sure the product is set up properly:
    ###############
    #INSTRUMENT:
    new_instrument = False
    try:
        instrument = Instrument.objects.get(id=raw_instrument['instrument']['id'])
        instrument.name=raw_instrument['instrument']['name']
        instrument.description=raw_instrument['instrument']['description']
        instrument.slug_name=raw_instrument['instrument']['slug_name']
        #TRANSLATIONS
        #NB
        instrument.name_nb=raw_instrument['instrument']['name_nb']
        instrument.description_nb=raw_instrument['instrument']['description_nb']
        instrument.slug_name_nb=raw_instrument['instrument']['slug_name_nb']
        instrument.save()
        logger.warning("... ... ... instrument already exists.")

    except Instrument.DoesNotExist as err:
        instrument = Instrument(
                id=raw_instrument['instrument']['id'],
                name=raw_instrument['instrument']['name'],
                description=raw_instrument['instrument']['description'],
                slug_name=raw_instrument['instrument']['slug_name'],
                #NB
                name_nb=raw_instrument['instrument']['name_nb'],
                description_nb=raw_instrument['instrument']['description_nb'],
                slug_name_nb=raw_instrument['instrument']['slug_name_nb']
            )
        instrument.save()
        new_instrument = True
        logger.warning("... ... ... instrument didn't already exists.")
        logger.warning("... ... ... so it was created.")

    ############
    #SCALE:

    scales=[]
    #make scales only if its a new instrument
    if new_instrument == True:
        logger.warning("... ... ... making the scales for the new instrument.")
        for scale in raw_instrument['scales']:
            if scale['type'] == "RatioScale":
                new_scale = RatioScale(
                    name=scale['name'],
                    instruction=scale['instruction'],
                    opt_out=scale['opt_out'],
                    min_value=scale['min_value'],
                    max_value=scale['max_value'],
                    min_value_description=scale['min_value_description'],
                    max_value_description=scale['max_value_description'],
                    #Translations
                    #NB
                    instruction_nb=scale['instruction_nb'],
                    min_value_description_nb=scale['min_value_description_nb'],
                    max_value_description_nb=scale['max_value_description_nb']
                )
                new_scale.save()
                scales.append(new_scale)
            else:
                raise ValueError("scale['%s'] provided, but not supported. Try 'RatioScale'."%(scale['type']))
    else:
        logger.warning("... ... ... adapting the scales for the existing instrument (only minor changes allowed).")
        for scale in raw_instrument['scales']:
            if scale['type'] == "RatioScale":
                try:
                    #grab the scale based on what not to be changed!
                    existing_scale = RatioScale.objects.get(
                        name=scale['name'],
                        min_value=scale['min_value'],
                        max_value=scale['max_value']
                    )
                    #some minor changes are allowed
                    existing_scale.instruction=scale['instruction']
                    existing_scale.opt_out=scale['opt_out']
                    existing_scale.min_value_description=scale['min_value_description']
                    existing_scale.max_value_description=scale['max_value_description']
                    #Translations
                    #NB
                    existing_scale.instruction_nb=scale['instruction_nb']
                    existing_scale.min_value_description_nb=scale['min_value_description_nb']
                    existing_scale.max_value_description_nb=scale['max_value_description_nb']

                    #save changes
                    existing_scale.save()
                    #add to scales for further processing
                    scales.append(existing_scale)
                except RatioScale.DoesNotExist as err:
                    raise IntegrityError(\
                        "Something was changed in the raw_data for scale %s in instrument %s, which SHOULD NOT be changed! ('name', 'min_value' or 'max_value')")

    assert len(scales) == len(raw_instrument['scales'])
    logger.warning("... ... ... done.")

    ################
    #DIMENSIONS


    #add actual Instrument and Scale objects to raw_data
    for d in raw_instrument['dimensions']:
        real_inst = Instrument.objects.get(id=d['instrument_id'])
        real_scale = scales[d['scale_location']]
        d['instrument'] = real_inst
        d['scale'] = real_scale

    #Make dimensions ONLY if this is a new instrument
    if new_instrument == True:
        logger.warning("... ... ... making dimensions for the new instrument.")
        for d in raw_instrument['dimensions']:
            new_d = Dimension(
                instrument=d['instrument'],
                name=d['name'],
                description=d['description'],
                scale=d['scale'],
                #TRANSLATIONS
                #NB
                name_nb=d['name_nb'],
                description_nb=d['description_nb']
            )
            new_d.save()
        logger.warning("... ... ... done.")

    #We may change some attributes of old dimensions, but only description right now
    if new_instrument == False:
        logger.warning("... ... ... looking to make minor modifications to dimensions (if any).")
        for d in raw_instrument['dimensions']:
            try:
                existing_d = Dimension.objects.get(instrument=d['instrument'], name=d['name'])
                #minor changes
                existing_d.description = d['description']
                #translations
                existing_d.name_nb=d['name_nb']
                existing_d.description_nb=d['description_nb'] 
                existing_d.save()
            except Dimension.DoesNotExist as err:
                    logger.info(
                    "%s %s %s dashboard_view: Small whoopsie. Couldn't find a dimension for the instrument %s with the name %s. Don't worry though, everything should work, but dimension names cannot be changed, and so long as the raw_data dimension name does not match the name in the database, other changes may not be made during setup of the instrument."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, d['instrument'], d['name']))
        logger.warning("... ... ... done.")
    dimensions = Dimension.objects.filter(instrument=instrument)
    assert len(dimensions) == len(raw_instrument['dimensions']), "Somehow we have ended up with %s dimensions for %s-instrument, while trying to have %s. Probably you changed the raw_data for the survey, but setup_instrument doesnt change dimensions for existing Instruments."%(len(dimensions), instrument.name, len(raw_instrument['dimensions']))

    ######
    #ITEMS
    #add dimension paramter to items from dimension_location

    for i in raw_instrument['items']:
        real_dimension = dimensions[i['dimension_location']]
        i.update({'dimension': real_dimension})

    #make a list with DB Item objects for all Items in raw_items
    logger.warning("... ... ... adding items if needed.")
    items=[]
    for ritem in raw_instrument['items']:
        #real_dimension = dimensions[ritem['dimension_location']]

        try:
            i = Item.objects.get(
                dimension=ritem['dimension'],
                formulation=ritem['formulation'],
                active=ritem['active'],
                inverted=ritem['inverted']
            )
            logger.warning("... ... ... ... found existing item with id %s, no need to make a new item."%(i.id))
            #TRANSLATIONS
            #NB
            i.formulation_nb = ritem['formulation_nb']
            i.save()
        except Item.DoesNotExist:
            i = Item(
                dimension=ritem['dimension'],
                formulation=ritem['formulation'],
                active=ritem['active'],
                inverted=ritem['inverted'],
                #TRANSLATIONS
                #NB
                formulation_nb=ritem['formulation_nb']

            )
            i.save()
            logger.warning("... ... ... ... made an item with id %s."%(i.id))

        finally:
            items.append(i)
    logger.warning("... ... ... done.")

    #Make sure there are no extra Items claiming to beloing to our dimensions (let's say a change was made, the old Item will stil be here)
    all_items = instrument.get_items()

    if len(all_items) != len(raw_instrument['items']):
        for i in all_items:
            if i not in items:
                i.delete()
    items = instrument.get_items()
    assert len(items) == len(raw_instrument['items']), "Somehow we have ended up with %s items for %s-instrument, while trying to have %s."%(len(items), instrument.name, len(raw_instrument['items']))
    logger.warning("... ... ... exiting setup_instrument() having made or updated the instrument %s, with id %s."%(instrument.name, instrument.id))
