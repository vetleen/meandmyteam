

#instrument
instrument_id = 1#THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
instrument = {
    'id': instrument_id, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
    'name': "Employee Engagement",
    'slug_name': "employee-engagement",
    'description': "An instrument that measures employee engagement",

    'name_nb': 'Ansattengasjement',
    'slug_name_nb': "ansattengasjement",
    'description_nb': "Et instrument som måler ansattengasjement",

}

#Scale
scale001 = {
    'type': "RatioScale",
    'name':"How often? Scale of One to Five",
    'instruction':"Please indicate how frequently the following occurs on a scale from one (never) to five (always):",
    'opt_out': True,
    'min_value': 1,
    'max_value': 5,
    'min_value_description':"never",
    'max_value_description':"always",
    #TRANSLATIONS
    #NB
    'instruction_nb':"Vennligst indiker hvor ofte det følgende er tilfelle, på en skala fra en (aldri) til fem (alltid):",
    'min_value_description_nb':"aldri",
    'max_value_description_nb':"alltid",
}
scales = [scale001, ]

#Dimensions
vigor = {
    'instrument_id': instrument_id,
    'name': "Vigor",
    'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
    'scale_location': 0, #index of the scales-variable (list) where the scale is located
    #Translations
    #NB
    'name_nb': "Pågangsmot",
    'description_nb': "Pågangmot kjennetegnes av et høyt energinivå, høy mental utholdenhet mens mann jobber, viljen til å investere innsats i arbeidet og at man holder ut, også når det blir vanskelig.",
}

dedication = {
    'instrument_id': instrument_id,
    'name': "Dedication",
    'description': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
    'scale_location': 0, #index of the scales-variable (list) where the scale is located
    #Translations
    #NB
    'name_nb': "Dedikasjon",
    'description_nb': "Dedikasjon kjennetegnes av en følelse av viktighet, entusiasme, inspirasjon, stolthet og utfordring, og kalles noen ganger for \"Innvolvering\".",
}
absorption = {
    'instrument_id': instrument_id,
    'name': "Absorption",
    'description': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
    'scale_location': 0, #index of the scales-variable (list) where the scale is located
    #Translations
    #NB
    'name_nb': "Innlevelse",
    'description_nb': "Innlevelse karakteriseres av at man er fullt ut konsentrert og fordypet i arbeidet man gjør, tiden går fort, og det er vanskelig å koble seg fra jobben. Å være fult absorbert i arbeidet kommer nærme det som kalles 'flow', en tilstand av optimal tilstedeværelse som er karakterisert av fokusert oppmerksomhet, klarhet i sinn, kropp-og-sinn sammensmeltning, det er enkelt å konsentrere seg, komplett kontroll, tap av selvbevisthet, tiden fly, og man nyter det man gjør.",
}
dimensions = [vigor, dedication, absorption]

#Items
i001 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "When I get up in the morning, I feel like going to work.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Når jeg står opp om morgenen, har jeg lyst til å gå på jobb.",
}

i002 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "At my work, I feel bursting with energy.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Når jeg er på jobb, har jeg masse energi",
}

i003 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "At my work I always persevere, even when things do not go well.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "På jobb så holder jeg alltid ut, selv når ting ikke går så bra.",
}

i004 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I can continue working for very long periods at a time.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg kan fortsette å jobbe i veldig lange sammenhengende perioder.",
}

i005 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "At my job, I am very resilient, mentally.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "På jobb er jeg mentalt veldig motstandsdyktig.",
}

i006 = {
    'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
    'formulation': "At my job I feel strong and vigorous.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "På jobb føler jeg med sterk og full av pågangsmot.",
}

i007 = {
    'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
    'formulation': "To me, my job is challenging.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg blir utfordret på jobben min.",
}

i008 = {
    'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
    'formulation': "My job inspires me.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jobben min inspirerer meg",
}

i009 = {
    'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I am enthusiastic about my job.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg er entusiastisk ovenfor jobben min",
}

i010 = {
    'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I am proud on the work that I do.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg er stolt over jobben som jeg gjør.",
}

i011 = {
    'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I find the work that I do full of meaning and purpose.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg finner at jobben jeg gjør er full av mening.",
}

i012 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "When I am working, I forget everything else around me.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Når jeg jobber, glemmer jeg alt annet rundt meg.",
}

i013 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "Time flies when I am working.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Tiden flyr når jeg jobber.",
}

i014 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I get carried away when I am working.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg blir revet med når jeg jobber",
}

i015 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "It is difficult to detach myself from my job.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Det er vanskelig å koble meg av jobben.",
}

i016 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I am immersed in my work.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg er fordypet i arbeidet mitt.",
}

i017 = {
    'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
    'formulation': "I feel happy when I am working intensely.",
    'active': True,
    'inverted': False,

    #TRANSLATION
    #NB
    'formulation_nb': "Jeg føler meg lykkelig når jeg jobber intenst.",
}
items = [
    i001, i002, i003, i004,
    i005, i006, i007, i008,
    i009, i010, i011, i012,
    i013, i014, i015, i016,
    i017
    ]

employee_engagement_instrument = {
    'instrument': instrument,
    'scales': scales,
    'dimensions': dimensions,
    'items': items,
}
