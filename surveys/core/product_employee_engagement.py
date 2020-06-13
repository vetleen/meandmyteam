from classes import Item, Dimension, Instrument

#Items for the "vigor" Dimension
vigor_item_01 = Item(
        formulation="When I get up in the morning, I feel like going to work.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

vigor_item_02 = Item(
        formulation="At my work, I feel bursting with energy.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

vigor_items=[vigor_item_01, vigor_item_02]

#Items for the "dedication" Dimension
dedication_item_01 = Item(
        formulation="To me, my job is challenging.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

dedication_item_02 = Item(
        formulation="My job inspires me.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

dedication_items=[dedication_item_01, dedication_item_02]

#Items for the "absorption" Dimension
absorption_item_01 = Item(
        formulation="When I am working, I forget everything else around me.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

absorption_item_02 = Item(
        formulation="Time flies when I am working.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        options=[1, 2, 3, 4, 5]
    )

absorption_items=[absorption_item_01, absorption_item_02]

#Dimensions for the "Employee Engagement" Instrument
vigor = Dimension(
        name="Vigor",
        description="",
        item_list=vigor_items
    )
dedication = Dimension(
        name="Dedication",
        description="",
        item_list=dedication_items
    )
absorption = Dimension(
        name="Absorption",
        description="",
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
for item in employee_engagement_instrument.get_items():
    print(item.dimension, ": ", item.formulation)
