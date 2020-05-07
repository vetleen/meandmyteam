from django.core.management.base import BaseCommand, CommandError
from surveys.models import Product, Question

class Command(BaseCommand):
    help = 'Makes the Product objects currently avilable'
    print("This command makes the Products if there are none.")
    print("Found %s Product objects"%(len(Product.objects.all())))

    def handle(*args, **kwargs):
        if len(Product.objects.all()) == 0:
            print("...making a product.")
            p = Product(
                name = 'Employee Satisfaction Tracking',
                short_description = ''
            )
            p.save()

            print("...making a question.")
            q1=Question(
                product = p,
                active = True,
                question_string = 'It is clear to me what is expected of me at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "role"
            )
            q1.save()

            print("...making a question.")
            q2=Question(
                product = p,
                active = True,
                question_string = 'I can decide when to take a break',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q2.save()

            print("...making a question.")
            q3=Question(
                product = p,
                active = True,
                question_string = 'Different groups at work demand different things from me that are hard to combine',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q3.save()

            print("...making a question.")
            q4=Question(
                product = p,
                active = True,
                question_string = 'I know how to go about getting my job done',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "role"
            )
            q4.save()

            print("...making a question.")
            q5=Question(
                product = p,
                active = True,
                question_string = 'I am subject to personal harassment in the form of unkind words or behaviour',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "relationships"
            )
            q5.save()

            print("...making a question.")
            q6=Question(
                product = p,
                active = True,
                question_string = 'I have unachievable deadlines',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q6.save()


            print("...making a question.")
            q7=Question(
                product = p,
                active = True,
                question_string = 'If work gets difficult, my colleagues will help me',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "peer support"
            )
            q7.save()

            print("...making a question.")
            q8=Question(
                product = p,
                active = True,
                question_string = 'I am given supportive feedback on the work I do',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "manager support"
            )
            q8.save()

            print("...making a question.")
            q9=Question(
                product = p,
                active = True,
                question_string = 'I have to work very intensively',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q9.save()

            print("...making a question.")
            q10=Question(
                product = p,
                active = True,
                question_string = 'I have a say in my own work speed',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q10.save()

            print("...making a question.")
            q11=Question(
                product = p,
                active = True,
                question_string = 'It is clear to me what my duties and responsibilities are',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "role"
            )
            q11.save()

            print("...making a question.")
            q12=Question(
                product = p,
                active = True,
                question_string = 'I have to neglect some tasks because I have too much to do',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q12.save()

            print("...making a question.")
            q13=Question(
                product = p,
                active = True,
                question_string = 'The goals and objectives for my department are clear to me',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "role"
            )
            q13.save()

            print("...making a question.")
            q14=Question(
                product = p,
                active = True,
                question_string = 'There is friction or anger between colleagues',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "relationships"
            )
            q14.save()

            print("...making a question.")
            q15=Question(
                product = p,
                active = True,
                question_string = 'I have a choice in deciding how I do my work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q15.save()

            print("...making a question.")
            q16=Question(
                product = p,
                active = True,
                question_string = 'I am unable to take sufficient breaks',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q16.save()


            print("...making a question.")
            q17=Question(
                product = p,
                active = True,
                question_string = 'I understand how my work fits into the overall aim of the organisation',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "role"
            )
            q17.save()

            print("...making a question.")
            q18=Question(
                product = p,
                active = True,
                question_string = 'I am pressured to work long hours',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q18.save()

            print("...making a question.")
            q19=Question(
                product = p,
                active = True,
                question_string = 'I have a choice in deciding what I do at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q19.save()

            print("...making a question.")
            q20=Question(
                product = p,
                active = True,
                question_string = 'I have to work very fast',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q20.save()

            print("...making a question.")
            q21=Question(
                product = p,
                active = True,
                question_string = 'I am subject to bullying at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "relationships"
            )
            q21.save()

            print("...making a question.")
            q22=Question(
                product = p,
                active = True,
                question_string = 'I have unrealistic time pressures',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "demands"
            )
            q22.save()

            print("...making a question.")
            q23=Question(
                product = p,
                active = True,
                question_string = 'I can rely on my manager to help me out with a work problem',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "manager support"
            )
            q23.save()

            print("...making a question.")
            q24=Question(
                product = p,
                active = True,
                question_string = 'I get help and support I need from colleagues',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "peer support"
            )
            q24.save()

            print("...making a question.")
            q25=Question(
                product = p,
                active = True,
                question_string = 'I have some say over the way I work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q25.save()

            print("...making a question.")
            q26=Question(
                product = p,
                active = True,
                question_string = 'I have sufficient opportunities to question managers about change at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "change"
            )
            q26.save()

            print("...making a question.")
            q27=Question(
                product = p,
                active = True,
                question_string = 'I receive the respect at work I deserve from my colleagues',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "peer support"
            )
            q27.save()

            print("...making a question.")
            q28=Question(
                product = p,
                active = True,
                question_string = 'Staff are always consulted about change at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "change"
            )
            q28.save()

            print("...making a question.")
            q29=Question(
                product = p,
                active = True,
                question_string = 'I can talk to my manager about something that has upset or annoyed me about work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "manager support"
            )
            q29.save()

            print("...making a question.")
            q30=Question(
                product = p,
                active = True,
                question_string = 'My working time can be flexible',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "control"
            )
            q30.save()

            print("...making a question.")
            q31=Question(
                product = p,
                active = True,
                question_string = 'My colleagues are willing to listen to my work-related problems',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "peer support"
            )
            q31.save()

            print("...making a question.")
            q32=Question(
                product = p,
                active = True,
                question_string = 'When changes are made at work, it is clear to me how they will work out in practice',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "change"
            )
            q32.save()

            print("...making a question.")
            q33=Question(
                product = p,
                active = True,
                question_string = 'I am supported through emotionally demanding work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "manager support"
            )
            q33.save()

            print("...making a question.")
            q34=Question(
                product = p,
                active = True,
                question_string = 'Relationships at work are strained',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "relationships"
            )
            q34.save()

            print("...making a question.")
            q35=Question(
                product = p,
                active = True,
                question_string = 'My manager encourages me at work',
                instruction_string ='How strongly do you agree with this statement?  1 means you don\'t  agree at all, and 5 means you agree completely.',
                dimension = "manager support"
            )
            q35.save()

            print("...done.")
        else:
            print ("... not making any products.")
        print("exiting.")
