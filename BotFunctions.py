#BotFunctions.py
from datetime import datetime
import pytz
import collections


TZONES = collections.defaultdict(set)
ABBREVS = collections.defaultdict(set)

for name in pytz.all_timezones:
    tzone = pytz.timezone(name)
    for utcoffset, dstoffset, tzabbrev in getattr(
            tzone, '_transition_info', [[None, None, 
                datetime.now(tzone).tzname()]]):
        TZONES[tzabbrev].add(name)
        ABBREVS[name].add(tzabbrev)

#############################
# FUNCTIONS 
#############################

"""
doConvertTimezone - Convert a time from one timezone to another.
    Parms:
        intime:         The time to be converted
        begtimezone     The timezone that the 'intime' parm is currently in
        endtimezone     The timezone to convert the time to
    Returns:
        The converted time IN STRING FORM
"""
def doConvertTimezone(intime, begtimezone, endtimezone):
    begtimezone = begtimezone.upper()
    endtimezone = endtimezone.upper()
    #Need to convert timezone?
    global TZONES
    if len(begtimezone) <= 3:
        begtimezone = next(iter(TZONES[begtimezone])).upper()
    if len(endtimezone) <= 3:
        endtimezone = next(iter(TZONES[endtimezone])).upper()

    begtimezone = pytz.timezone(begtimezone)
    endtimezone = pytz.timezone(endtimezone)

    intime = datetime.strptime(intime, "%Y-%m-%d %H:%M:%S")
    intime = begtimezone.localize(intime)
    intime = intime.astimezone(endtimezone)
    intime = intime.strftime("%Y-%m-%d %H:%M:%S")

    return intime
#end doConvertTimezone function

"""
doTimeDiff - Get the difference between two different times.
    Parms:
        future:     The time that is further in the future.
        past:       The time that is further in the past.
    Returns:
        Array of values: hours, minutes and seconds between the two times.
"""
def doTimeDiff(future, past):
    difference = future - past
    diff_in_s = difference.total_seconds()
    calcd = divmod(diff_in_s, 3600)
    hours = calcd[0]
    calcd = divmod(calcd[1], 60)
    minutes = calcd[0]
    seconds = calcd[1]
    retlist = [hours, minutes, round(seconds)]
    return retlist
#end doTimeDiff function

"""
doPhaseLeft - Get how much time is left in the current phase.
    Parms:
        ctx:    The bot functions.
    Returns:
        A dict of values:
            "success":      whether we successfully returned the proper values.
            "messageinfo":  The information to give to the user.
            "hours":        The hours left in the phase.
            "minutes":      The minutes left in the phase.
            "seconds":      The seconds left in the phase.
*(note: the mins & secs do not include the hours, i.e. it won't be above 60)
"""
async def doPhaseLeft(ctx):
    global PHASE_END_TIME
    global PHASE_END_TIMEZONE
    if PHASE_END_TIME == "":
        message_info = await ctx.send ("No phase set!")
        return {
            "success": False,
            "messageinfo": message_info,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
    phaseendtime = datetime.strptime(doConvertTimezone(PHASE_END_TIME, 
        PHASE_END_TIMEZONE, "EST"), "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if now >= phaseendtime:
        message_info = await ctx.send ("TIME IS UP!")
        return {
            "success": False,
            "messageinfo": message_info,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
    timelist = doTimeDiff(phaseendtime, now)
    hours = timelist[0]
    minutes = timelist[1]
    seconds = timelist[2]
    message_info = await ctx.send("Time remaining: " + str(round(hours)) + 
        " hours, " + str(round(minutes)) + " minutes and " + str(seconds) + 
        " seconds")
    return {
            "success": True,
            "messageinfo": message_info,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }
#end doPhaseLeft function

# def getGlobalData(id):