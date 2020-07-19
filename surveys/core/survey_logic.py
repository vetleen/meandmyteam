from surveys.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import datetime
import os

#set up logging
import logging
logger = logging.getLogger('__name__')

def configure_survey_setting(organization, instrument, **kwargs):
    #Assert that we received valid input
    if not isinstance(organization, Organization):
        raise TypeError(
            "configure_survey_setting() takes an argument 'organization' that must be an instance of models. Organziation, but was %s"\
            %(type(organization))
        )
    if not isinstance(instrument, Instrument):
        raise TypeError(
            "configure_survey_setting() takes an argument 'instrument' that must be an instance of models. Instrument, but was %s"\
            %(type(instrument))
        )

    #make sure we have a SurveySetting object to work with:
    try:
        ss = SurveySetting.objects.get(organization=organization, instrument=instrument)
    except SurveySetting.DoesNotExist as err:
        ss = SurveySetting(organization=organization, instrument=instrument)
        ss.save()

    #look for kwargs and update accordingly
    if 'is_active' in kwargs:
        new_is_active = kwargs.get('is_active', None)
        assert isinstance(new_is_active, bool)
        ss.is_active = new_is_active

    if 'survey_interval' in kwargs:
        new_survey_interval = kwargs.get('survey_interval', None)
        assert isinstance(new_survey_interval, int)
        ss.survey_interval = new_survey_interval

    if 'surveys_remain_open_days' in kwargs:
        new_surveys_remain_open_days = kwargs.get('surveys_remain_open_days', None)
        assert isinstance(new_surveys_remain_open_days, int)
        ss.surveys_remain_open_days = new_surveys_remain_open_days

    #if 'last_survey_open' in kwargs:
    #    new_last_survey_open = kwargs.get('last_survey_open', None)
    #    assert isinstance(new_last_survey_open, datetime.date) and not isinstance(new_last_survey_open, datetime.datetime)
    #    ss.last_survey_open = new_last_survey_open

    #if 'last_survey_close' in kwargs:
    #    new_last_survey_close = kwargs.get('last_survey_close', None)
    #    assert isinstance(new_last_survey_close, datetime.date) and not isinstance(new_last_survey_close, datetime.datetime)
    #    ss.last_survey_close = new_last_survey_close

    #ensure that dates are updated
    ss.check_last_survey_dates()

    #save all changes
    ss.save()
    return ss

#create a new survey
def create_survey(owner, instrument_list, **kwargs):
    #assert that correct inputs were given
    ##check required inputs
    assert isinstance(owner, Organization), \
        "'owner' must be an Organization object, but was %s"%(type(owner))
    assert isinstance(instrument_list, list), \
        "'instrument_list' must be a list, but was %s"%(type(instrument_list))
    assert len(instrument_list)>0, \
        "'instrument_list' must have items in it, but was empty"
    for instrument in instrument_list:
        assert isinstance(instrument, Instrument), \
            "items in 'instrument_list' must be Instrument objects, but was %s"%(type(instrument))
        try:
            ss = SurveySetting.objects.get(organization=owner, instrument=instrument)
        except SurveySetting.DoesNotExist as err:
            raise AssertionError(
                "'instrument' %s is not configured for 'organization' %s"%(instrument, organization))

    ##check optional input (and make sure we have date_open and _close variables)
    date_open = None
    date_close = None
    if 'date_open' in kwargs:
        assert isinstance(date_open, datetime.date), \
            "'date_open' must be datetime object, was %s"%(type(date_open))
        date_close = kwargs.get('date_open', None)

    if 'date_close' in kwargs:
        assert isinstance(date_close, datetime.date), \
            "'date_close' must be datetime object, was %s"%(type(date_close))
        date_close = kwargs.get('date_close', None)

    #other assertions
    ##Check that there are no open surveys for the same organization already
    open_surveys = Survey.objects.filter(owner=owner, is_closed=False)
    assert len(open_surveys) < 1, \
        "Could not create_survey() because one or more surveys are already open for this organization"

    ##Check settings for is_active and time since last, and grab survey interval to use
    survey_remain_open_days = 0
    for instrument in instrument_list:
        #grab settings
        survey_setting = configure_survey_setting(owner, instrument)

        #Check that instrument is active for this Org
        assert survey_setting.is_active == True, \
            "Could not create_survey() because an instrument in the instrument_list (%s) provided was not an active instrument for this organization (%s)"\
            %(instrument, owner)

        #find the longest remain_open_time of all their instruments and use that
        if survey_remain_open_days < survey_setting.surveys_remain_open_days:
            survey_remain_open_days = survey_setting.surveys_remain_open_days


    #if date_open and date_close was not provided, make sure they are set
    if date_open is None:
        date_open = datetime.date.today()
    if date_close is None:
        date_close = date_open + datetime.timedelta(days=survey_remain_open_days)

    #create the survey object
    survey = Survey(
        owner=owner,
        date_open=date_open,
        date_close=date_close
    )
    survey.save()

    #Update settings with new data
    for instrument in instrument_list:
        #update the last_survey_open- and last_survey_close dates

        survey_setting = configure_survey_setting(owner, instrument)

        #add survey to instrument.surveys (m2m-list)
        survey_setting.surveys.add(survey)
        survey_setting.check_last_survey_dates()

    #create the SurveyItems that go with this object
    for instrument in instrument_list:
        for i in instrument.get_items():

            #Create RatioSurveyItem when RatioScale is in use
            if isinstance(i.dimension.scale, RatioScale):
                rsi = RatioSurveyItem(
                    survey=survey,
                    item_formulation=i.formulation,
                    item_inverted=i.inverted,
                    item_dimension=i.dimension
                )
                rsi.save()
            #Create other scale types as they are implemented....
            #elif isinstance (i.dimension.scale...
            else:
                logger.warning(
                    "%s %s: %s: tried to make SurveyItems for a new survey, but one of the Items (\"%s\") in the supplied Instrument has a self.dimension.scale that is faulty: %s."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, i, i.dimension.scale)
                )
    #create the dimensionresult objects, that will be used to store results when the survey is closed
    for instrument in instrument_list:
        for dimension in instrument.dimension_set.all():
            if isinstance(dimension.scale, RatioScale):
                rsdr = RatioScaleDimensionResult(survey=survey, dimension=dimension)
                rsdr.save()
            #elif isinstance (dimension.scale...
            else:
                logger.warning(
                    "%s %s: %s: tried to make RatioScaleDimensionResult for a new survey, but one of the Dimensions (\"%s\") in the supplied Instrument has a self.scale that is faulty: %s."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, dimension, dimension.dimension.scale)
                )

    return survey



#create the SurveyInstances
def survey_instances_from_survey(survey):
    #assert that valid inputs were given
    assert isinstance(survey, Survey), \
        "'survey' must be a Survey object, but was %s"%(type(survey))

    #check that it IS an open survey
    if survey.is_closed == True:
        logger.warning(
            "%s %s: %s: tried to make survey_instances from survey, but it was already closed. (%s with id: %s)"\
            %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, survey, survey.id)
        )
        return

    #make survey instances for all employee's that doesn't already have one

    respondent_list = Respondent.objects.filter(organization=survey.owner)
    for r in respondent_list:
        try:
            #check if we already have a surveyinstance
            si = SurveyInstance.objects.get(survey=survey, respondent=r)
        except SurveyInstance.DoesNotExist as err:
            #if we don't already have one, make one
            si = SurveyInstance(survey=survey, respondent=r)
            si.save()
            #add items
            survey_items = survey.get_items()
            for i in survey_items:
                #Create RatioSurveyInstanceItems when RatioScale is in use
                if isinstance(i, RatioSurveyItem):
                    rsii = RatioSurveyInstanceItem(
                        survey_instance=si,
                        survey_item=i,
                    )
                    rsii.save()
                #elif
                    #create other items....:
                else:
                    #catchall, if some items were'nt processed by any of the above categories
                    logger.warning(
                        "%s %s: %s: tried to make SurveyInstanceItems for a new surveyInstance, but one of the Items (\"%s\") in the supplied Survey has a 'self.item_dimension.scale' that is faulty: %s."\
                        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, i, i.item_dimension.scale)
                    )
    #update number of invited for survey
    si_list = SurveyInstance.objects.filter(survey=survey)
    survey.n_invited = len(si_list)
    survey.save()
    return si_list

def answer_item(survey_instance_item, answer):
    #validate input
    assert isinstance(survey_instance_item, SurveyInstanceItem), \
        "'survey_instance_item' must be a SurveyInstanceItem object, but was %s"%(type(survey_instance_item))
    if isinstance(survey_instance_item, RatioSurveyInstanceItem):
        assert isinstance(answer, int), \
            "'answer' to a RatioSurveyInstanceItem must be an int, but was %s"%(type(answer))

    #answer the item
    survey_instance_item.answer = answer
    survey_instance_item.answered = True
    survey_instance_item.save()

    #make sure the survey instance is marked as started
    if survey_instance_item.survey_instance.started==False:
        survey_instance_item.survey_instance.started=True
        survey_instance_item.survey_instance.save()

    #return it for future use
    return survey_instance_item

def close_survey(survey):
    #validate input
    assert isinstance(survey, Survey), \
        "'survey' must be a Survey object, but was %s"%(type(survey_instance_item))

    #set surveys date_close to be at the latest yesterday
    if survey.date_close >= datetime.date.today(): #if it was set in the future
        survey.date_close = datetime.date.today()+datetime.timedelta(days=-1)

    #mark as closed
    survey.is_closed = True

    #grab survey instances for this survey
    si_list = SurveyInstance.objects.filter(survey=survey)

    #prepare to count complete and incomplete SIs
    n_completed = 0
    n_incomplete = 0
    n_not_started = 0

    #go through every SI to 1) make averages and 2) determine if it was started and/or completed
    for si in si_list:
        #get items for SurveyInstance
        sii_list = si.get_items()

        #make up status of entire SurveyInstance, to be counted further down...
        was_began = False
        was_completed = True
        for sii in sii_list:
            if sii.answered == True:
                was_began=True
            else:
                was_completed=False

        #count completed and update SI in db
        if was_completed == True:
            si.completed = True
            si.started = True
            n_completed += 1
        elif was_began == True:
            si.completed = False
            si.started = True
            n_incomplete += 1
        else:
            si.completed = False
            si.started = False
            n_incomplete += 1
        #save survey_instance
        si.save()

    #add the data to the survey object
    survey.n_completed = n_completed
    survey.n_incomplete = n_incomplete
    survey.n_not_started = n_not_started

    #save the survey
    survey.save()

    #Time to summarize each SurveyItem and DimensionResult

    #go through each dimension in the survey to calculate and store results of survey
    sdr_list = survey.dimensionresult_set.all()
    for dr in sdr_list:
        #if this is a RatioScaled dimension:
        if isinstance(dr, RatioScaleDimensionResult):

            #Calculate averages and completed-states for each SurveyItem
            rsitem_list = RatioSurveyItem.objects.filter(item_dimension=dr.dimension)
            for rsitem in rsitem_list:
                #get all SurveyInstanceItems for this SurveyItem
                sii_list = RatioSurveyInstanceItem.objects.filter(survey_item=rsitem)
                #initiate counters
                rsitem_total = 0
                rsitem_n = 0
                rsitem_avg = 0
                #go through and grab the numbers needed to close the item
                for sii in sii_list:
                    if sii.answered==True:
                        #only count answered
                        rsitem_total += sii.answer
                        rsitem_n += 1
                #find the average for the SurveyItem
                if rsitem_n > 0:
                    rsitem_avg = (rsitem_total/rsitem_n)
                #save the average if this SurveyItem to the db
                rsitem.average = rsitem_avg
                rsitem.n_answered = rsitem_n
                rsitem.save()

            #Calculate avergaes and completed-states for each dimension

            #initiate counters
            rsdr_total = 0
            rsdr_n = 0
            rsdr_n_items = 0
            rsdr_avg = 0
            #look at every surveyinstance to see if the dimension was completed
            sinstance_list = SurveyInstance.objects.filter(survey=survey)
            for sinstance in sinstance_list:
                #set defaults be changed when proven oherwise
                sinstance_dimension_total = 0
                sinstance_dimension_n = 0
                dimension_completed = True
                #go through each question for the survey instance and see if they completed:
                rsii_list = RatioSurveyInstanceItem.objects.filter(survey_instance=sinstance)
                for rsii in rsii_list:
                    if rsii.dimension() == dr.dimension:
                        if rsii.answered == True:
                            sinstance_dimension_total += rsii.answer
                            sinstance_dimension_n += 1
                        else:
                            dimension_completed = False
                            break
                #if the dimension was completed for this survey, add the results to the dimension-totals
                if dimension_completed == True:
                    rsdr_total += sinstance_dimension_total
                    rsdr_n_items += sinstance_dimension_n
                    rsdr_n += 1
            #now we can calculate the total avg
            if rsdr_n_items > 0:
                rsdr_avg = (rsdr_total/rsdr_n_items)
            #save average for this DimensionResult to DB
            dr.average=rsdr_avg
            dr.n_completed=rsdr_n
            dr.save()

        #elif isinstance(dr,
            #do things to other scaled dimensions
        else:
            #catchall, if a DimensionResult wasn't processed by any of the above categories
            logger.warning(
                "%s %s: %s: tried to close a SurveyDimension (\"%s\") in the supplied Survey, but its subclass was not recognized: %s."\
                %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, dr, type(dr))
            )
    #return survey for future use
    return survey

def get_results_from_survey(survey, instrument, get_previous=True):
    #validate input
    assert isinstance(survey, Survey), \
        "'survey' must be a Survey object, but was %s"%(type(survey))
    assert isinstance(instrument, Instrument), \
        "'instrument' must be a Instrument object, but was %s"%(type(instrument))
    assert isinstance(get_previous, bool), \
        "'get_previous' must be a bool, but was %s"%(type(get_previous))

    def get_previous_survey_w_instrument(survey, instrument):
        '''
        Will return the last survey before survey that answered the dimensions in instrument, or None if none exists.
        '''
        #validate input
        assert isinstance(survey, Survey), \
            "'survey' must be a Survey object, but was %s"%(type(survey))
        assert isinstance(instrument, Instrument), \
            "'instrument' must be a Instrument object, but was %s"%(type(instrument))

        #grab the latest survey
        previous_surveys = Survey.objects.filter(owner=survey.owner, date_close__lt=survey.date_close).order_by('-date_close')[:1]

        #print("get_previous_survey_w_instrument was called with survey %s"%(survey))
        #print("previous survey is: %s."%(previous_surveys))

        #if there wasn't any previuous surveys, return None
        if len (previous_surveys) < 1:
            return None
        else:
            previous_survey = previous_surveys[0]

        #check if this survey measured the dimensions of the instrument
        idimensions = [d for d in instrument.dimension_set.all()]
        psdimensions = [dr.dimension for dr in previous_survey.dimensionresult_set.all()]
        is_same = True
        for d in idimensions:
            if d not in psdimensions:
                is_same = False

        #if the same, return , if not, go deeper
        if is_same == True:
            return previous_survey
        else:
            return get_previous_survey_w_instrument(survey=previous_survey, instrument=instrument)


    #get results from previous survey
    previous_data = None
    if get_previous == True:
        #get previous survey
        previous_survey = get_previous_survey_w_instrument(survey=survey, instrument=instrument)

        #get results from previous survey
        if previous_survey is not None:
            previous_data = get_results_from_survey(survey=previous_survey, instrument=instrument, get_previous=False)

    #instantiate dict to be returned
    data = {
        'instrument': instrument,
        'survey': survey,
        'dimension_results': [],
        'item_results': [],
        'previous_data': previous_data,
    }
    if survey.is_closed == False:
        return data

    #get results from dimensions and add to our instrument_data
    dr_list = survey.dimensionresult_set.all()
    instrument_dimensions = [d for d in instrument.dimension_set.all()]

    #prep search for highest/lowest RSDR
    highest_average_rsdr = None
    highest_average_rsdr_value = 0
    lowest_average_rsdr = None
    lowest_average_rsdr_value = None

    #go through DR and add to data if DR belongs to instrument
    for dr in dr_list:
        if dr.dimension in instrument_dimensions:
            if isinstance(dr, RatioScaleDimensionResult):
                #determine the lowest and highest RSDR, to be included in data
                if dr.average is not None:
                    if highest_average_rsdr_value is None:
                        highest_average_rsdr = dr
                        highest_average_rsdr_value = dr.average
                    else:
                        if dr.average > highest_average_rsdr_value:
                            highest_average_rsdr = dr
                            highest_average_rsdr_value = dr.average

                    if lowest_average_rsdr_value is None:
                        lowest_average_rsdr = dr
                        lowest_average_rsdr_value = dr.average
                    else:
                        if dr.average < lowest_average_rsdr_value:
                            lowest_average_rsdr = dr
                            lowest_average_rsdr_value = dr.average

                #give full data if enough respondents
                if dr.n_completed > 3:
                    #percent_of_max
                    percent_of_max = (((dr.average-dr.dimension.scale.min_value)/(dr.dimension.scale.max_value-dr.dimension.scale.min_value)))*100
                    #if previous data, get the changes
                    change_average = None
                    change_percent_of_max = None
                    red_bar = None
                    green_bar = None
                    blue_bar = None
                    #but only if the previous numbers can be shown
                    if previous_data is not None:
                        for pdr in previous_data['dimension_results']:
                            if pdr['dimension'] == dr.dimension:
                                if pdr['average'] is not None:
                                    previous_average = pdr['average']
                                    change_average = dr.average-previous_average

                                if pdr['percent_of_max'] is not None:
                                    previous_percent_of_max = pdr['percent_of_max']
                                    change_percent_of_max = percent_of_max-previous_percent_of_max
                                    #make the bar lengths to display (maybe this should be in view?)
                                    if change_percent_of_max > 0:
                                        red_bar = 0
                                        green_bar = change_percent_of_max
                                        blue_bar = previous_percent_of_max
                                    elif change_percent_of_max == 0:
                                        red_bar = 0
                                        green_bar = 0
                                        blue_bar = 0
                                    else:
                                        red_bar = -change_percent_of_max
                                        green_bar = 0
                                        blue_bar = percent_of_max
                    #add data
                    dr_data = {
                        'dimension': dr.dimension,
                        'scale': dr.dimension.scale,
                        'n_completed': dr.n_completed,
                        'average': dr.average,
                        'percent_of_max': percent_of_max,
                        'change_average': change_average,
                        'change_percent_of_max': change_percent_of_max,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                        'blue_bar': blue_bar,
                        'highest_average': None,
                        'lowest_average': None
                    }
                #give limited data if NOT enough respondents
                else:
                    dr_data = {
                        'dimension': dr.dimension,
                        'scale': dr.dimension.scale,
                        'n_completed': dr.n_completed,
                        'average': None,
                        'percent_of_max': None,
                        'change_average': None,
                        'change_percent_of_max': None,
                        'red_bar': None,
                        'green_bar': None,
                        'blue_bar': None,
                        'highest_average': None,
                        'lowest_average': None

                    }

                data['dimension_results'].append(dr_data)
            #elif.... other DR types than RatioScale
            else:
                logger.warning(
                    "%s %s: %s: tried to get results from a DimensionResults (\"%s\") in the supplied Survey, but its subclass was not recognized: %s."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, dr, type(dr))
                )
    #Now that we know the best and worst score, add that into the DR
    if highest_average_rsdr != None and lowest_average_rsdr != None: #We should always have both or neither
        for dr in data['dimension_results']:
            if dr['dimension'] == highest_average_rsdr.dimension:
                dr['highest_average'] = True
            else:
                dr['highest_average'] = False
            if dr['dimension'] == lowest_average_rsdr.dimension:
                dr['lowest_average'] = True
            else:
                dr['lowest_average'] = False

    #get data from items and add to our data, if item belongs to our instrument
    item_list = survey.get_items()
    for i in item_list:
        if i.item_dimension in instrument_dimensions:
            if isinstance(i, RatioSurveyItem):
                #give full data if enough respondents
                if i.n_answered > 3:
                    i_data = {
                        'formulation': i.item_formulation,
                        'dimension': i.item_dimension,
                        'scale': i.item_dimension.scale,
                        'inverted': i.item_inverted,
                        'n_answered': i.n_answered,
                        'percent_of_max': (((i.average-i.item_dimension.scale.min_value)/(i.item_dimension.scale.max_value-i.item_dimension.scale.min_value)))*100,
                        'average': i.average
                    }
                    #print(i_data)
                #give limited data if NOT enough respondents
                else:
                    i_data = {
                        'formulation': i.item_formulation,
                        'dimension': i.item_dimension,
                        'scale': i.item_dimension.scale,
                        'inverted': i.item_inverted,
                        'n_answered': i.n_answered,
                        'percent_of_max': None,
                        'average': None
                    }
                data['item_results'].append(i_data)
                #item_data_list.append(i_data)
            else:
                logger.warning(
                    "%s %s: %s: tried to get results from a SurveyItem (\"%s\") in the supplied Survey, but its subclass was not recognized: %s."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, i, type(i))
                )

    #deliver data
    return data

def get_results_from_instrument(instrument, organization, depth=None):
    #validate input
    assert isinstance(instrument, Instrument), \
        "'instrument' must be an Instrument object, but was %s"%(type(instrument))
    assert isinstance(organization, Organization), \
        "'organization' must be an Organization object, but was %s"%(type(organization))
    if depth is not None:
        assert isinstance(depth, int), \
            "'depth' must be an integer, but was %s"%(type(depth))

    #get survey_setting
    try:
        survey_setting = SurveySetting.objects.get(instrument=instrument, organization=organization)
    except SurveySetting.DoesNotExist as err:
        #if there is no survey_setting, there is no surveys
        #print("error: %s"%(err))
        return None

    #check if any open surveys, and if so add 1 to depth
    open_surveys_list = survey_setting.surveys.filter(is_closed=False)
    if len(open_surveys_list) > 0:
        depth += len(open_surveys_list)

    #get surveys from survey_settings, sorted by date and cut off at depth
    if depth is not None:
        surveys = survey_setting.surveys.all().order_by('-date_close')[:depth] #the first item is the latest survey
    else:
        surveys = survey_setting.surveys.all().order_by('-date_close') #the first item is the latest survey

    #return None if no surveys
    if len(surveys) < 1:
        return None

    #instantiate dict to be returned
    data = {
        'instrument': instrument,
        'surveys': []
    }

    #get data from surveys and add to data
    for survey in surveys:
        survey_results = get_results_from_survey(survey, instrument)
        data['surveys'].append(survey_results)

    #deliver data
    return data

#automatically create surveys when due
def create_survey_if_due(organization):
    '''
    Looks at an organization and creates a survey with all due instruments, if
    any. If none are due, it does nothing.
    '''
    #assert that valid inputs were given
    assert isinstance(organization, Organization), \
        "'organization' must be a Organization object, but was %s"%(type(organization))

    #grab settings
    survey_setting_list = SurveySetting.objects.filter(organization=organization)
    #Make a list of due instruments
    active_and_due_survey_setting_list = []
    active_but_not_due_survey_setting_list = []
    #sort out the settings for instruments that are active and due
    for survey_setting in survey_setting_list:
        #ensure that it's up to date
        survey_setting.check_last_survey_dates()
        #continue
        if survey_setting.is_active == True:
            if survey_setting.last_survey_open is None:
                active_and_due_survey_setting_list.append(survey_setting)
            else:
                next_survey_due_date = survey_setting.last_survey_open+datetime.timedelta(days=survey_setting.survey_interval)
                if datetime.date.today() > next_survey_due_date:
                    active_and_due_survey_setting_list.append(survey_setting)
                else:
                    active_but_not_due_survey_setting_list.append(survey_setting)
    #create the list of survey_settings that we will make surveys for, begin with those that are due and active
    due_survey_setting_list = active_and_due_survey_setting_list
    #check active, but not due ones, if they are "close enough" to add in
    if len(due_survey_setting_list) > 0:
        for survey_setting in active_but_not_due_survey_setting_list:
            #Is this instrument due within half of the interval?, if so proceed...
            next_survey_due_date = survey_setting.last_survey_open+datetime.timedelta(days=survey_setting.survey_interval)
            if next_survey_due_date < datetime.date.today()+datetime.timedelta(days=(survey_setting.survey_interval/2)):
                #Is it also due in the next 60 days, if so add it to the current survey
                if next_survey_due_date < datetime.date.today()+datetime.timedelta(days=60):
                    due_survey_setting_list.append(survey_setting)

    #create the survey
    if len(due_survey_setting_list) > 0:

        survey = create_survey (
            owner=organization,
            instrument_list=[survey_setting.instrument for survey_setting in due_survey_setting_list]
        )
        return survey
    return None

def close_survey_if_date_close_has_passed(survey):
    #validate input
    assert isinstance(survey, Survey), \
        "'survey' must be a Survey object, but was %s"%(type(survey))
    assert survey.is_closed == False, \
        "this survey was already closed"
    assert survey.date_close < datetime.date.today(), \
        "It is not yet time to close this survey, it will close %s."%(survey.date_close)

    #close the survey
    survey = close_survey(survey)
    #return the now closed survey
    return survey


def send_email_for_survey_instance(survey_instance):
    """ Takes a survey_instance and sends an email to it's respondent if it is time """
    #validate input
    assert isinstance(survey_instance, SurveyInstance), \
        "'survey_instance' must be a SurveyInstance object, but was %s"%(type(survey_instance))
    assert survey_instance.survey.is_closed == False, \
        "'survey_instance' must belong to an open survey"

    #define the function that actually sends the emails
    def create_and_send_single_email_about_survey_instance(survey_instance, email_txt_template, email_html_template, subject_template):
        #validate input
        assert isinstance(survey_instance, SurveyInstance), \
            "'survey_instance' must be a SurveyInstance object, but was %s"%(type(survey_instance))

        #Make a Token so the Respondent can find the instance
        url_token = survey_instance.get_url_token()

        #Get a string representation fon the owner of the Survey
        contact_person = survey_instance.survey.owner.owner
        contact_person_str = contact_person.email
        if contact_person.first_name !='' and contact_person.last_name !='':
            contact_person_str = '%s %s'%(survey_instance.survey.owner.owner.first_name, survey_instance.survey.owner.owner.last_name)

        #find out the topics covered
        instrument_list = []
        dimension_result_list = survey_instance.survey.dimensionresult_set.all()
        for dr in dimension_result_list:
            if dr.dimension.instrument not in instrument_list:
                instrument_list.append(dr.dimension.instrument)


        #prepare context to be passed into the email
        context={
                'token': url_token,
                'organization': survey_instance.survey.owner.name,
                'contact_person': contact_person_str,
                'instrument_list': instrument_list,
                'hostname': 'www.motpanel.com'#os.environ.get('HOSTNAME', 'www.motpanel.com')
                }
        #print (os.environ)
        #gather content for the email
        subject=render_to_string(subject_template, context).rstrip("\n\r")
        text_content=render_to_string(email_txt_template, context)
        html_content=render_to_string(email_html_template, context)
        from_email='surveys@motpanel.com'
        to=[survey_instance.respondent.email]

        #make and send email
        email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
        return email_message

    def configure_and_call_send_email(email_txt_template, email_html_template, subject_template, category):
        #validate input
        assert isinstance(email_txt_template, str), \
            "'email_txt_template' must be of the type string, but was"%(type(email_txt_template))
        assert isinstance(email_html_template, str), \
            "'email_html_template' must be of the type string, but was"%(type(email_html_template))
        assert isinstance(subject_template, str), \
            "'subject_template' must be of the type string, but was"%(type(subject_template))
        assert isinstance(category, str), \
            "'category' must be of the type string, but was"%(type(category))
        assert category in RespondentEmail.ALLOWED_CATEGORIES, \
            "'category' %s was not found in allowed categories, %s."%(category, RespondentEmail.ALLOWED_CATEGORIES)
        #create and send email
        try:
            email_message = create_and_send_single_email_about_survey_instance(
                survey_instance=survey_instance,
                email_txt_template=email_txt_template,
                email_html_template=email_html_template,
                subject_template=subject_template,
            )
            assert isinstance(email_message, EmailMultiAlternatives), \
                "send_email_about_survey_instance returned %s, but expected an instance of EmailMultiAlternatives"%(type(email_message))
            #log success
            respondent_email = RespondentEmail(
                survey_instance=survey_instance,
                email_date = datetime.date.today(),
                category = category,
                error_message=None
            )
            respondent_email.save()
            return respondent_email

        except AssertionError as err:
            #log error
            respondent_email = RespondentEmail(
                survey_instance=survey_instance,
                email_date = datetime.date.today(),
                category = 'failure',
                error_message=err
            )
            respondent_email.save()
            return respondent_email

    #if this survey_instance was already completed, don't send anything
    if survey_instance.check_completed() == True:
        return None

    #an initial invitation should be sent out if it hasn't already been done
    try:
        initial_email = survey_instance.respondentemail_set.get(category='initial')
    except RespondentEmail.DoesNotExist:
        initial_email = configure_and_call_send_email(
            email_txt_template='emails/new_survey_instance_email_txt.html',
            email_html_template='emails/new_survey_instance_email_html.html',
            subject_template='emails/new_survey_subject.txt',
            category='initial'
        )
        if initial_email.category == 'failure':
            logger.warning(
                "%s %s: %s: Tried to send 'initial' email to %s about the survey %s, but failed."\
                %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, survey_instance.respondent.email, survey_instance.survey)
            )
        return initial_email

    #Deal with reminders
    #some settings for reminders
    max_reminders_per_survey = 2
    send_last_reminder_date = survey_instance.survey.date_close + datetime.timedelta(days=-1)
    #print("Going to send last reminder on %s"%(send_last_reminder_date))
    remind_after_days = 3
    #see what's been sent before
    email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure') #the first shall be the last (latest email_date)
    #print("email_list has a length of %s"%(len(email_list)))
    #don't send more emails than max reminders + 1 (for the 'inital')
    if len(email_list) >= max_reminders_per_survey+1:
        #print("too many reminders, return None")
        return None
    #also, don't send more reminders if the 'last_chance' email has gone out
    elif email_list[0].category == 'last_chance':
        #print("last chance was already sent out, return None")
        return None
    #send last_chance if that date has come
    elif datetime.date.today() >= send_last_reminder_date:
        last_chance_email = configure_and_call_send_email(
            email_txt_template='emails/last_chance_survey_instance_email_txt.html',
            email_html_template='emails/last_chance_survey_instance_email_html.html',
            subject_template='emails/last_chance_survey_subject.txt',
            category='last_chance'
        )
        if last_chance_email.category == 'failure':
            logger.warning(
                "%s %s: %s: Tried to send 'last chance' email to %s about the survey %s, but failed."\
                %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, survey_instance.respondent.email, survey_instance.survey)
            )
        return last_chance_email
    #or, send normal reminder if max reminders have not been reached (saving one for 'last_chance', AND if some time has passed since the last email)
    elif len(email_list) <= max_reminders_per_survey-1 and datetime.date.today() >= (email_list[0].email_date+datetime.timedelta(days=remind_after_days)):
        reminder_email = configure_and_call_send_email(
            email_txt_template='emails/remind_survey_instance_email_txt.html',
            email_html_template='emails/remind_survey_instance_email_html.html',
            subject_template='emails/remind_survey_subject.txt',
            category='reminder'
        )
        if reminder_email.category == 'failure':
            logger.warning(
                "%s %s: %s: Tried to send 'reminder' email to %s about the survey %s, but failed."\
                %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, survey_instance.respondent.email, survey_instance.survey)
            )
        return reminder_email
    #or, ...?
    else:
        #print("catchall, return None")
        return None
