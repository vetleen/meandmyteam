complete_products_list = []

class Product:
    def __init__(self, number, name, short_description):
        for p in complete_products_list:
            assert p.number != number, "Product number must be unique"
        self.number = number
        self.name = name
        self.short_description = short_description
        self.question_list=[]

    def __str__(self):
        """String for representing the Product object (in Admin site etc.)."""
        return self.name

class Question:
    ''' Questions belong to products '''
    def __init__(self, question_string, dimension=None, active=True):

        question_string = question_string
        dimension = dimension
        active = active

    def __str__(self):
        """String for representing the Question object (in Admin site etc.)."""
        return self.question_string


employee_satisfaction_tracking = Product(
    number = 1,
    name = 'Employee Satisfaction Tracking',
    short_description = ''
)

complete_products_list.append(employee_satisfaction_tracking)

q1=Question(

    active = True,
    question_string = 'It is clear to me what is expected of me at work',
    dimension = "role"
)
employee_satisfaction_tracking.question_list.append(q1)
'''
q2=Question(
    product = p,
    active = True,
    question_string = 'I can decide when to take a break',
    dimension = "control"
)
q2.save()


q3=Question(
    product = p,
    active = True,
    question_string = 'Different groups at work demand different things from me that are hard to combine',
    dimension = "demands"
)
q3.save()


q4=Question(
    product = p,
    active = True,
    question_string = 'I know how to go about getting my job done',
    dimension = "role"
)
q4.save()


q5=Question(
    product = p,
    active = True,
    question_string = 'I am subject to personal harassment in the form of unkind words or behaviour',
    dimension = "relationships"
)
q5.save()


q6=Question(
    product = p,
    active = True,
    question_string = 'I have unachievable deadlines',
    dimension = "demands"
)
q6.save()



q7=Question(
    product = p,
    active = True,
    question_string = 'If work gets difficult, my colleagues will help me',
    dimension = "peer support"
)
q7.save()


q8=Question(
    product = p,
    active = True,
    question_string = 'I am given supportive feedback on the work I do',
    dimension = "manager support"
)
q8.save()


q9=Question(
    product = p,
    active = True,
    question_string = 'I have to work very intensively',
    dimension = "demands"
)
q9.save()


q10=Question(
    product = p,
    active = True,
    question_string = 'I have a say in my own work speed',
    dimension = "control"
)
q10.save()


q11=Question(
    product = p,
    active = True,
    question_string = 'It is clear to me what my duties and responsibilities are',
    dimension = "role"
)
q11.save()


q12=Question(
    product = p,
    active = True,
    question_string = 'I have to neglect some tasks because I have too much to do',
    dimension = "demands"
)
q12.save()


q13=Question(
    product = p,
    active = True,
    question_string = 'The goals and objectives for my department are clear to me',
    dimension = "role"
)
q13.save()


q14=Question(
    product = p,
    active = True,
    question_string = 'There is friction or anger between colleagues',
    dimension = "relationships"
)
q14.save()


q15=Question(
    product = p,
    active = True,
    question_string = 'I have a choice in deciding how I do my work',
    dimension = "control"
)
q15.save()


q16=Question(
    product = p,
    active = True,
    question_string = 'I am unable to take sufficient breaks',
    dimension = "demands"
)
q16.save()



q17=Question(
    product = p,
    active = True,
    question_string = 'I understand how my work fits into the overall aim of the organisation',
    dimension = "role"
)
q17.save()


q18=Question(
    product = p,
    active = True,
    question_string = 'I am pressured to work long hours',
    dimension = "demands"
)
q18.save()


q19=Question(
    product = p,
    active = True,
    question_string = 'I have a choice in deciding what I do at work',
    dimension = "control"
)
q19.save()


q20=Question(
    product = p,
    active = True,
    question_string = 'I have to work very fast',
    dimension = "demands"
)
q20.save()


q21=Question(
    product = p,
    active = True,
    question_string = 'I am subject to bullying at work',
    dimension = "relationships"
)
q21.save()


q22=Question(
    product = p,
    active = True,
    question_string = 'I have unrealistic time pressures',
    dimension = "demands"
)
q22.save()


q23=Question(
    product = p,
    active = True,
    question_string = 'I can rely on my manager to help me out with a work problem',
    dimension = "manager support"
)
q23.save()


q24=Question(
    product = p,
    active = True,
    question_string = 'I get help and support I need from colleagues',
    dimension = "peer support"
)
q24.save()


q25=Question(
    product = p,
    active = True,
    question_string = 'I have some say over the way I work',
    dimension = "control"
)
q25.save()


q26=Question(
    product = p,
    active = True,
    question_string = 'I have sufficient opportunities to question managers about change at work',
    dimension = "change"
)
q26.save()


q27=Question(
    product = p,
    active = True,
    question_string = 'I receive the respect at work I deserve from my colleagues',
    dimension = "peer support"
)
q27.save()


q28=Question(
    product = p,
    active = True,
    question_string = 'Staff are always consulted about change at work',
    dimension = "change"
)
q28.save()


q29=Question(
    product = p,
    active = True,
    question_string = 'I can talk to my manager about something that has upset or annoyed me about work',
    dimension = "manager support"
)
q29.save()


q30=Question(
    product = p,
    active = True,
    question_string = 'My working time can be flexible',
    dimension = "control"
)
q30.save()


q31=Question(
    product = p,
    active = True,
    question_string = 'My colleagues are willing to listen to my work-related problems',
    dimension = "peer support"
)
q31.save()


q32=Question(
    product = p,
    active = True,
    question_string = 'When changes are made at work, it is clear to me how they will work out in practice',
    dimension = "change"
)
q32.save()


q33=Question(
    product = p,
    active = True,
    question_string = 'I am supported through emotionally demanding work',
    dimension = "manager support"
)
q33.save()


q34=Question(
    product = p,
    active = True,
    question_string = 'Relationships at work are strained',
    dimension = "relationships"
)
q34.save()


q35=Question(
    product = p,
    active = True,
    question_string = 'My manager encourages me at work',
    dimension = "manager support"
)
q35.save()
'''
