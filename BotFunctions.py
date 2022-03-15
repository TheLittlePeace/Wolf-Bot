#BotFunctions.py
from datetime import datetime
import pytz
import collections
import os
import psycopg2
from dotenv import load_dotenv
from discord.utils import get
from ErrorHandler import *

load_dotenv()

TZONES = collections.defaultdict(set)
ABBREVS = collections.defaultdict(set)
PGPW = os.getenv('POSTGRESQL_PASSWORD')
PGCONN = psycopg2.connect(
    host = "localhost",
    database = "TWG",
    user = "postgres",
    password = PGPW
)

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
def doConvertTimezone(intime: str, begtimezone: str, endtimezone: str):
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
def doTimeDiff(future: str, past: str):
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
    phaseendtime = getGlobalData("PHASEENDTIME")
    if(phaseendtime == None):
        await customError("Phase End Not Found!")
        return
    phaseendtzone = getGlobalData("PHASEENDTZONE")
    if(phaseendtzone == None):
        await customError("Phase End Not Found!")
        return
    if phaseendtime == "":
        message_info = await ctx.send ("No phase set!")
        return {
            "success": False,
            "messageinfo": message_info,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
    phaseendtime = datetime.strptime(doConvertTimezone(phaseendtime, 
        phaseendtzone, "EST"), "%Y-%m-%d %H:%M:%S")
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

"""
getGlobalData - Retrieve a global data variable from the database.
    Parms:
        id: The variable to retrieve.
    Returns:
        The data requested, IN STRING FORM, or None if it failed.
"""
def getGlobalData(id: str):
    global PGCONN
    cur = PGCONN.cursor()
    id = id.upper().strip()
    cur.execute("SELECT data FROM globaldatastore WHERE id = %s", (id,))
    ret = cur.fetchone()
    if(ret == None):
        return False
    ret = ret[0]
    return ret
#end getGlobalData function

"""
setGlobalData - Set a global data variable in the database.
    Parms:
        id: The variable ID to save.
        data: The variable data to save.
    Returns:
        True if successful, False otherwise.
"""
def setGlobalData(id: str, data: str):
    global PGCONN
    cur = PGCONN.cursor()
    id = id.upper().strip()
    data = data.strip()

    #See if it exists already.
    cur.execute("SELECT data FROM globaldatastore WHERE id = %s", (id,))
    ret = cur.fetchone()
    if(ret == None):
        #Write
        cur.execute("INSERT INTO globaldatastore (id, data) VALUES(%s, %s)", 
            (id, data))
    else:
        #Update
        cur.execute("UPDATE globaldatastore SET data = %s WHERE id = %s", 
            (data, id))

    #Check to see if it worked
    cur.execute("SELECT data FROM GlobalDataStore WHERE id = %s", (id,))
    ret = cur.fetchone()
    if(ret == None):
        return False
    PGCONN.commit()
    return True
#end setGlobalData

"""
setUser - Sets a member's user up in the database
    Parms:
        username: The member's username
        userid: The member's user ID
    Returns:
        True if successful, False otherwise.
"""
def setUser(username: str, userid: int):
    global PGCONN
    cur = PGCONN.cursor()
    cur.execute("INSERT INTO members(username, userid) VALUES (%s, %s)",
        (username.strip(), str(userid)))
    
    #Check to see if it worked
    cur.execute("SELECT userid FROM members WHERE username = %s", (username,))
    ret = cur.fetchone()
    if(ret == None):
        return False
    PGCONN.commit()
    return True
#end setUser

"""
getUserID - Retrieve the user's ID based on a name provided
    Parms:
        name: The name to retrieve. Can be username or nickname that's stored.
    Returns:
        The user's ID integer, or False if it failed.
"""
def getUserID(name: str):
    global PGCONN
    cur = PGCONN.cursor()
    sqlstmt = """SELECT userid
        FROM members mbr
        LEFT JOIN members_nicknames nck
            ON mbr.id = nck.memberid
        WHERE UPPER(nickname) = UPPER(%s)
            OR UPPER(username) = UPPER(%s)"""
    cur.execute(sqlstmt, (name, name))
    ret = cur.fetchone()
    if(ret == None):
        return False
    ret = ret[0]
    return ret
#end getUserID
    
"""
giveRole - Give a user a specified role
    Parms:
        ctx:    The bot functions.
        name:   The user to set the role of. Can be username or nickname.
        role:   The name of the role to be given, as stored in GlobalDataStore.
    Returns:
        True if successful, error message otherwise.
"""
async def giveRole(ctx, name: str, role: str):
    userid = getUserID(name)
    if(userid == False):
        return "User " + name + " not found! Check spelling and try again."
    roleid = int(getGlobalData(role))
    if(roleid == False):
        return "Role " + role + " not found! Check spelling and try again."
    user = await ctx.guild.fetch_member(userid)
    roleobj = get(ctx.guild.roles, id = roleid)
    await user.add_roles(roleobj)
    return True
#end giveRole

"""
removeRole - Remove a user's specified role
    Parms:
        ctx:    The bot functions.
        Name:   The user to remove the role from. Username or nickname.
        role:   The role to be removed, as stored in GlobalDataStore.
    Returns:
        True if successful, error message otherwise.
"""
async def removeRole(ctx, name:str, role:str):
    userid = getUserID(name)
    if(userid == False):
        return "User " + name + " not found! Check spelling and try again."
    roleid = int(getGlobalData(role))
    if(roleid == False):
        return "Role " + role + " not found! Check spelling and try again."
    user = await ctx.guild.fetch_member(userid)
    roleobj = get(ctx.guild.roles, id = roleid)
    await user.remove_roles(roleobj)
    return True
#end removeRole