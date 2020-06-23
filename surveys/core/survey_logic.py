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

    ##Check settings for * is_active * time since last * grab survey interval to use
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
    s = Survey(
        owner=owner,
        date_open=date_open,
        date_close=date_close
    )
    s.save()

    #ensure we update the last_survey_open- and last_survey_close dates in settings for all instruments
    for instrument in instrument_list:
        survey_setting = configure_survey_setting(owner, instrument, last_survey_open=date_open, last_survey_close=date_close)

    #create the SurveyItems that go with this object
    for instrument in instrument_list:
        for i in instrument.get_items():

            #Create RatioSurveyItem when RatioScale is in use
            if isinstance(i.dimension.scale, RatioScale):
                rsi = RatioSurveyItem(
                    survey=s,
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
                rsdr = RatioScaleDimensionResult(survey=s, dimension=dimension)
                rsdr.save()
            #elif isinstance (dimension.scale...
            else:
                logger.warning(
                    "%s %s: %s: tried to make RatioScaleDimensionResult for a new survey, but one of the Dimensions (\"%s\") in the supplied Instrument has a self.scale that is faulty: %s."\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, dimension, dimension.dimension.scale)
                )

    return s



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
                    #print(rsii.dimension())
                    #print(dr.dimension)
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
                    rsdr_n += sinstance_dimension_n

            #now we can calculate the total avg
            if rsdr_n > 0:
                rsdr_avg = (rsdr_total/rsdr_n)

            #save average for this DimensionResult to DB
            dr.average=rsdr_avg
            dr.n_completed=rsdr_n
            dr.save()




        #elif isinstance(dr,
            #do things to other scaled dimensions
        else:
            #catchall, if a DimensionResult wasn't processed by any of the above categories
            logger.warning(
                "%s %s: %s: tried to make SurveyInstanceItems for a new surveyInstance, but one of the Items (\"%s\") in the supplied Survey has a 'self.item_dimension.scale' that is faulty: %s."\
                %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, i, i.item_dimension.scale)
            )






    #return survey for future use
    return survey
