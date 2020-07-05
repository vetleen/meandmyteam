def create_test_data(instrument_id):
    instrument = {
        'id': instrument_id, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
        'name': "Employee Engagement",
        'slug_name': "employee_engagement",
        'description': "An instrument that measures employee engagement"
    }

    #Scale
    scale001 = {
        'type': "RatioScale",
        'name':"How often? Scale of One to Five",
        'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
        'opt_out': True,
        'min_value': 1,
        'max_value': 5,
        'min_value_description':"never",
        'max_value_description':"always",
    }
    scales = [scale001, ]

    #Dimensions
    vigor = {
        'instrument_id': instrument_id,
        'name': "Vigor",
        'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }

    dedication = {
        'instrument_id': instrument_id,
        'name': "Dedication",
        'description': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }
    absorption = {
        'instrument_id': instrument_id,
        'name': "Absorption",
        'description': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }
    dimensions = [vigor, dedication, absorption]

    #Items
    i001 = {
        'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
        'formulation': "When I get up in the morning, I feel like going to work.",
        'active': True,
        'inverted': False,
    }

    i002 = {
        'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
        'formulation': "At my work, I feel bursting with energy.",
        'active': True,
        'inverted': False,
    }

    i007 = {
        'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
        'formulation': "To me, my job is challenging.",
        'active': True,
        'inverted': False,
    }

    i008 = {
        'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
        'formulation': "My job inspires me.",
        'active': True,
        'inverted': False,
    }

    i012 = {
        'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
        'formulation': "When I am working, I forget everything else around me.",
        'active': True,
        'inverted': False,
    }

    i013 = {
        'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
        'formulation': "Time flies when I am working.",
        'active': True,
        'inverted': False,
    }

    items = [i001, i002, i007, i008, i012, i013]

    raw_test_instrument = {
        'instrument': instrument,
        'scales': scales,
        'dimensions': dimensions,
        'items': items,
    }
    return raw_test_instrument
