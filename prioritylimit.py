'''
Created on 09/09/2012

@author: Ryan
'''
import sabnzbd.utils.configobj as configobj
import time
import urllib2
import json
import sys

path = "prioritylimit.ini"

try:
    CFG = configobj.ConfigObj(infile=path, raise_errors=True, file_error=True)
except configobj.ConfigObjError, strerror:
    print '"%s" is not a valid configuration file<br>Error message: %s' % (path, strerror)
    sys.exit(1)

# ini file should have the following:
# host = hostname and port
# apikey = apikey
# priority = limit (0 for no limit)
# refreshInterval=refreshinterval (seconds)
host = CFG["host"]

# api key is optional
apikey = None

if 'apikey' in CFG:
    apikey = CFG["apikey"]

refreshInterval = CFG["refreshInterval"]
logLevel = int(CFG["logLevel"])    

limits = {}
limits['Normal'] = CFG["normal"]
limits['High'] = CFG["high"]
limits['Low'] = CFG["low"]
limits['Force'] = CFG["force"]

def logWarn(logStr):
    if logLevel >= 2:
        print "WARNING: " + logStr

def logInfo(logStr):
    if logLevel >= 3:
        print "INFO: " + logStr

def logDebug(logStr):
    if logLevel >= 4:
        print "DEBUG: " + logStr

# main loop
logInfo("Monitoring host " + host)

lostServer = False

try:
    while True:
        # query server for top of the queue
        url = "http://" + host + "/sabnzbd/api?mode=queue&output=json"
        if apikey is not None:
            url = url + "&apikey=" + apikey
        
        logDebug(url)
        
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError:
            if not lostServer:
                logWarn("Could not contact host: " + host + ". Is host wrong or server not running?")
                lostServer = True
            
            time.sleep(int(refreshInterval))
            continue
        
        if lostServer:
            logInfo("Reconnected to host.")
            lostServer = False
        
        html = response.read()
        
        properties = json.loads(html)
        
        if 'error' in properties:
            print "Error response from host: " + properties['error']
            sys.exit(1)
        
        if 'queue' not in properties or 'slots' not in properties['queue']:
            print "Unexpected response from host: " + properties
            sys.exit(1)
        
        slots = properties['queue']['slots']
        
        if len(slots) < 1:
            logDebug("Nothing in queue.")
            time.sleep(int(refreshInterval))
            continue
        
        topPriority = slots[0]['priority']
        currentLimit = properties['queue']['speedlimit']
        
        logDebug("Current limit: " + str(currentLimit))
        logDebug("Limit for " + str(topPriority) + ": " + str(limits[topPriority]))
        
        if currentLimit != limits[topPriority]:
            logInfo("Updating limit to " + str(limits[topPriority]))
            logDebug("http://" + host + "/sabnzbd/api?apikey=" + apikey + "&mode=config&name=speedlimit&value=" + str(limits[topPriority]))
            urllib2.urlopen("http://" + host + "/sabnzbd/api?apikey=" + apikey + "&mode=config&name=speedlimit&value=" + str(limits[topPriority]))
        
        time.sleep(int(refreshInterval))
except KeyboardInterrupt:
    logInfo("Interrupted. Exiting...")
