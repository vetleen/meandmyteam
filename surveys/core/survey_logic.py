from surveys.models import *
import datetime

#set up logging
import logging
logger = logging.getLogger('__name__')

def configure_survey_setting(organization, instrument, **kwargs):
    #Assert that we received valid input
    if not isinstance(organization, Organization):
        raise TypeError(
            "configure_survey_setting() takes an argument 'organization' that must be an instance of models.Organziation, but was %s"\
            %(type(organization))
        )
    if not isinstance(instrument, Instrument):
        raise TypeError(
            "configure_survey_setting() takes an argument 'instrument' that must be an instance of models.Instrument, but was %s"\
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

    if 'last_survey_open' in kwargs:
        new_last_survey_open = kwargs.get('last_survey_open', None)
        assert isinstance(new_last_survey_open, datetime.date) and not isinstance(new_last_survey_open, datetime.datetime)
        ss.last_survey_open = new_last_survey_open

    if 'last_survey_close' in kwargs:
        new_last_survey_close = kwargs.get('last_survey_close', None)
        assert isinstance(new_last_survey_close, datetime.date) and not isinstance(new_last_survey_close, datetime.datetime)
        ss.last_survey_close = new_last_survey_close

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

        #check that enough time has elapsed since last survey was initiated
        if survey_setting.last_survey_open is not None:
            assert (survey_setting.last_survey_open+datetime.timedelta(days=survey_setting.survey_interval)) < datetime.date.today(), \
                "Could not create_survey() because it is too little time since we last surveyed %s with %s." \
                %(owner, instrument)

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
        survey_setting = configure_survey_setting(owner, instrument, last_survey_open=date_open, last_survey_close=date_close)

        #add survey to instrument.surveys (m2m-list)
        survey_setting.surveys.add(survey)

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

def get_results_from_survey(survey, instrument):
    #validate input
    assert isinstance(survey, Survey), \
        "'survey' must be a Survey object, but was %s"%(type(survey))
    assert isinstance(instrument, Instrument), \
        "'instrument' must be a Instrument object, but was %s"%(type(instrument))


    #instantiate list of results to be returned
    #instrument_results_list=[]

    #instantiate dict to be returned
    data = {
        'instrument': instrument,
        'survey': survey,
        'dimension_results': [],
        'item_results': []
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
                #determine the lowest and highest RSDR, to be included in data below, after for loop
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
                #print("Highest: %s (%s)"%(highest_average_rsdr_value, highest_average_rsdr))
                #print("Lowest: %s (%s)"%(lowest_average_rsdr_value, lowest_average_rsdr))
                #give full data if enough respondents
                if dr.n_completed > 3:
                    dr_data = {
                        'dimension': dr.dimension,
                        'scale': dr.dimension.scale,
                        'n_completed': dr.n_completed,
                        'average': dr.average,
                        'percent_of_max': (((dr.average-dr.dimension.scale.min_value)/(dr.dimension.scale.max_value-dr.dimension.scale.min_value)))*100,
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

def get_results_from_instrument(instrument, organization, depth):
    #validate input
    assert isinstance(instrument, Instrument), \
        "'instrument' must be an Instrument object, but was %s"%(type(instrument))
    assert isinstance(organization, Organization), \
        "'organization' must be an Organization object, but was %s"%(type(organization))
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
    surveys = survey_setting.surveys.all().order_by('-date_close')[:depth] #the first item is the latest survey

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



    #return dicts
