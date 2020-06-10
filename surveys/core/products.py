from base import Item, Dimension, Instrument

#Items for the "vigor" Dimension
vigor_item_01 = Item(
        formulation="When I get up in the morning, I feel like going to work.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        active=True,
        options=[1, 2, 3, 4, 5]
    )

vigor_item_02 = Item(
        formulation="At my work, I feel bursting with energy.",
        instruction_string="Please indicate the extent to which you agree on a scale from 1 to 5 where 5 means you strongly agree, and 1 means you don't agree at all.",
        active=True,
        options=[1, 2, 3, 4, 5]
    )
vigor_items=[vigor_item_01, vigor_item_02]


#Dimensions for the "Employee Engagement" Instrument
vigor = Dimension(
        name="Vigor",
        description="",
        item_list=vigor_items
    )
employee_engagement_dimensions = [vigor, ]

#Instruments
employee_engagement_instrument = Instrument(
        name = "Employee Engagement",
        description = "",
        dimension_list = employee_engagement_dimensions
    )



#DOES IT WORK?
for item in employee_engagement_instrument.get_items():
    print(item.dimension)
