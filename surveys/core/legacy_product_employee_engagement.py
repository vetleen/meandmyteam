from classes import Item, Dimension, Instrument, Scale

#Scale for the employee engagement product

#SCALES SHOULD NEVER BE DELETED! IF NECCESARY, ADD A NEW ONE, AND CHANGE THE
#REFERENCE IN THE DIMENSION, BUT NEVER REMOVE A SCALE, IT WILL BREAK SCORING OF
#OLD SURVEYS. OR WILL IT?
OneToFiveFrequencyScale = RatioScale(

        name='OneToFiveFrequencyScale',
        min_value = 1,
        max_value = 5,
        instruction_string="Please indicate from 1 (Never) to 5 (Always) how often the following is true:",
        min_value_description  = "Never",
        max_value_description = "Always"
    )

#Items for the "vigor" Dimension
vigor_item_01 = Item(
        formulation="When I get up in the morning, I feel like going to work.",
    )

vigor_item_02 = Item(
        formulation="At my work, I feel bursting with energy.",
    )

vigor_items=[vigor_item_01, vigor_item_02]

#Items for the "dedication" Dimension
dedication_item_01 = Item(
        formulation="To me, my job is challenging.",
    )

dedication_item_02 = Item(
        formulation="My job inspires me.",
    )

dedication_items=[dedication_item_01, dedication_item_02]

#Items for the "absorption" Dimension
absorption_item_01 = Item(
        formulation="When I am working, I forget everything else around me.",
    )

absorption_item_02 = Item(
        formulation="Time flies when I am working.",
    )

absorption_items=[absorption_item_01, absorption_item_02]

#Dimensions for the "Employee Engagement" Instrument
vigor = Dimension(
        name="Vigor",
        description="",
        scale=OneToFiveFrequencyScale,
        item_list=vigor_items
    )
dedication = Dimension(
        name="Dedication",
        description="",
        scale=OneToFiveFrequencyScale,
        item_list=dedication_items
    )
absorption = Dimension(
        name="Absorption",
        description="",
        scale=OneToFiveFrequencyScale,
        item_list=absorption_items
    )
employee_engagement_dimensions = [vigor, dedication, absorption]

#Instruments
employee_engagement_instrument = Instrument(
        name = "Employee Engagement",
        description = "",
        dimension_list = employee_engagement_dimensions
    )


#DOES IT WORK?
#for item in employee_engagement_instrument.get_items():
#    print(item.dimension, ": ", item.formulation)
