import sys
import math
import os
import os.path
import datetime
import pprint
#import urllib2
from http import HTTPClient
#import decimal
import StringIO
import time

# TODO: use open, high, low and close not just close price
# TODO: be able to filter on intra-day volatility (e.g. difference between low/high)
# TODO: gap analysis, e.g. today's close vs. tomorrows open
# TODO: calculate historical volatility over various time periods
# TODO: estimate future volatility based on historic vol over various time periods
#   see the Natenberg book for info on how to do this 

#RUT questions I can't answer
#what was biggest % drop in X days
#what was biggest % rise in X days
#What has historically happened the next day after -(0-5)%, -(2-8)%
#  this is similar to matching u or d
# There are multiple interpretations of the above. Sometimes we want to know what happened the next
# day after we had ONE DAY that was up between 2-4%, followed by another SINGLE DAY that was up 2-4%.
# Sometimes we want to know what happened in the N days following an N day period in which the underlying
# was up or down X%. 
#Accumulating +/-X% change
#  --how long does it take on average
#  --what was smallest number of days it took
# (e.g. if I know I lose money if RUT goes up 15% too quickly I want to know historically how long has it taken to gain 15% on average and what was the shortest time period it ever took to gain this much)
#Would be nice to be able to learn the same things about RVX, e.g. what's the fastest that vol has jumped over 5 points or 10%

# TODO: experimental matplotlib stuff
#from pylab import *
#from matplotlib.finance import candlestick, candlestick2

# how to automatically find promising patterns
#  hist 0 1 65
# want to consider both patterns that persist (so check entire date range, plus most recent half, plus most
#   recent quarter) and patterns that have developed more recently (last two years)
# TODO: more thoughts on this

# TODO: show total points in addition to min/max/avg
# TODO: for each pattern show how many times it occurred (updays+downdays) and % occurrence (updays+downdays/total days)*100.0
# TODO: use ncurses to show lines in colour
# keep a list of important dates (fed announcements, european bank, bank of england interest rate announcements)
#  and include those in patterns
#
# TODO: consider another way of forming patterns, instead of up/down days, look back N days and add up the total
# gain in points, use that as the 'pattern', then figure out how many up/down days result from that. For example
# if you have  +10,  -1,  +5,  -3, <TODAY>  and lookback is 3, then we'd use a key of -1+5-3=1 with today either U or D
# then we can generalise over time about what happens after 3 days of net 1 point.

# FTSE historical download
#  http://ichart.yahoo.com/table.csv?s=%5EFTSE&d=5&e=5&f=2007&g=d&a=3&b=2&c=1984&ignore=.csv
# RUT historical download
#  http://ichart.yahoo.com/table.csv?s=%5ERUT&d=5&e=5&f=2007&g=d&a=8&b=10&c=1987&ignore=.csv
# a,b,c are the start date
# d,e,f are the end date
# g is the data type: d, w, m, or v (daily, weekly, monthly, or dividends)
# s is the ticker symbol
# q is the output type: q for spreadsheet, h for HTML (use q)
# x is the output file extension, either .html or .txt or .csv (use .csv)
# TODO: create a long string out of UUDDUD and allow regex search, e.g.
#   U{3,}D{2} matches a string up 3 or more up days followed by 2 down days
#   match U{3,}D{2} [daterange]  find string of up/down days
#   find <lambda> allow specifying an expression
#   stats show general stats
#       up/down days by dow/day of month/month/last day of month
#       avg up/down % by dow/day of month/month/last day of month
# TODO: keep track of percentage change per day, and possibly moving averages
# TODO: allow saving session to file
# TODO: allow comparing one underlying to another
# TODO: allow charting a daterange by launching gnuplot or excel or matplotlib
# TODO: check chinese market against 'lucky'/'unlucky' numbers
#     see http://www.pekingduck.org/archives/000401.php
# TODO: get price distribution, plot price distribution, extra credit: plot vs. lognormal distribution
# TODO: some command that just let's it fly and try to find a bunch of good patterns, reusing hist
# TODO: when loading prices from disc, offer to refresh from internet if last day of history < yesterday
# TODO: avgaccum gives avg number of points accumulated in *exactly* <days>, maybe we should
# also have swings <days> that shows max swing in any time period up to <days>
"""
Things to try
  - how many mondays are up if the preceding friday is up?
  - allow specifying startdate/enddate for processing

    def loadFromYahoo(self, underlying):
    if USE_PROXY:
        proxyHandler = urllib2.ProxyHandler(
{"http":"http://%s:%s@primary-proxy:8080" % \
                (PROXY_USERNAME, PROXY_PASSWORD)})
        opener = urllib2.build_opener(proxyHandler,
urllib2.ProxyBasicAuthHandler(), urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    req = urllib2.Request("http://finance.yahoo.com/q/op?s=%s&m=%s-%s"
% (symbol, year, month))
    html = urllib2.urlopen(req).read()

    # TODO: remove this
    f = open(r".\\lastfetch.htm", "wb")
    f.write(html)
    f.close()
"""


MONTH = [None, "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
DOW = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
UPDAY = ["D", "U"]
def formatDate(date):
    return "%s %s.%02d.%02d" % (DOW[date.weekday()], date.year, date.month, date.day)

def findThirdFriday(year, month):
    """
    Find the date that is the 3rd friday of the month
    """
    date = datetime.date(year, month, 1)
    fridays = 0
    while True:
        if date.weekday() == 4:
            fridays += 1
            if fridays == 3:
                return date
        date = date + datetime.timedelta(days=1)

def dateInOptionExpirationWeek(date):
    """
    Return True if date occurs in an option expiration week.
    TODO: NOTE: assumes expiration week is always the week preceding the 3rd saturday of the month.
    This is not the case for currency options, etc..
    """
    friday = findThirdFriday(date.year, date.month)
    return date in [
        friday,
        friday - datetime.timedelta(days=1),
        friday - datetime.timedelta(days=2),
        friday - datetime.timedelta(days=3),
        friday - datetime.timedelta(days=4)]

class HistoryItem(object):
    def __init__(self, date, _open, high, low, _close, volume, prev):
        self.date = date
        self.open = _open
        self.high = high
        self.low = low
        self.close = _close
        self.volume = volume
        self.prev = prev
        
    gap = property(lambda self : self.open - self.prev.close)
    gappct = property(lambda self : self.gap / self.prev.close * 100.0)
    range = property(lambda self : self.high - self.low)
    upday = property(lambda self : self.close > self.prev.close)               
    ptschange = property(lambda self : self.close - self.prev.close)
    pctchange = property(lambda self : self.ptschange / self.prev.close * 100.0)

    def __repr__(self):
        return "%s: %3.2f/%3.2f/%3.2f/%3.2f %s %.2f (%.2f%%) gap %3.2f (%.2f%%)" % (formatDate(self.date), 
                                                                 self.open, self.high, self.low, self.close, 
                                                                 UPDAY[int(self.upday)], 
                                                                 self.ptschange, self.pctchange,
                                                                 self.gap, self.gappct)
    
    def __cmp__(self, other):
        return cmp(self.date, other.date)

#class StatsItem(object):
#    def __init__(self, updays, downdays, uptotal, downtotal):
#        self.updays = updays
#        self.downdays = downdays
#        self.uppct = (float(self.updays)/(self.updays + self.downdays)) * 100.0
#        self.downpct = 100.0 - self.uppct
#        self.uptotal = uptotal
#        self.downtotal = downtotal

class PriceAnalyzer(object):
    def __init__(self):
        self._startdate = datetime.date(1900, 01, 01)
        self._enddate = datetime.date.today()
        self._underlying = None
        self._data = None
        self._date_to_index = {}
        self._path = ".\\"
        self.verbose = False

    def load(self, underlying, filename):
        underlying = underlying.upper()
        if not os.path.exists(os.path.join(self._path, filename)):
            print "Local file '%s' not found, checking internet..." % filename
            try:
                self.getFromInternet(underlying, filename)
            except Exception, e:
                print "error: %s" % str(e)
                print "note: index symbols may need a ^ prefix"
                return
        #data = self.loadFromFile(filename)
        #dates = data.keys()
        #dates.sort()
        #print dates[0], dates[-1] # TODO:
        self._underlying = underlying
        data = [(date, _open, high, low, _close, volume) for (date, _open, high, low, _close, volume) \
                    in self.loadFromFile(filename)]
        data.sort()
        self._data = []
        prev = None
        for i, (date, _open, high, low, _close, volume) in enumerate(data):
            item = HistoryItem(date, _open, high, low, _close, volume, prev)
            if i > 0:
                #thisprice = data[date]
                #lastprice = data[dates[i-1]]
                #upday = (thisprice > lastprice)
                #ptschange = (thisprice - lastprice)
                #pctchange = ptschange / lastprice * 100.0
                self._data.append(item)
            prev = item
        self._date_to_index = dict([(item.date, i) for i, item in enumerate(self._data)])
        self.setDateRangeToAll()

    def getFromInternet(self, underlying, filename):
        today = datetime.date.today()
        url = "http://ichart.yahoo.com/table.csv?s=%s&a=00&b=1&c=1980&d=%s&e=%s&f=%s&g=d&ignore=.csv" % \
            (underlying, today.month-1, today.day, today.year)
        print "Getting '%s'" % url
#        try:
#            # e.g. http://username:password@primary-proxy:8080
#            proxy = open(".\\analyze_prices.proxy", "ru").read().strip()
#        except:
#            proxy = None
#        if proxy:
#            proxyHandler = urllib2.ProxyHandler({"http":proxy})
#            opener = urllib2.build_opener(proxyHandler, urllib2.ProxyBasicAuthHandler(), urllib2.HTTPHandler)
#            urllib2.install_opener(opener)
#        req = urllib2.Request(url)
#        data = urllib2.urlopen(req).read()
        
        c = HTTPClient(proxy="proxy2:3128")
        data = c.get(url)
        
        #print data
        #io = StringIO.StringIO(data)
        f = open(filename, "w")
        f.write(data)
        #for line in [x.split(",") for x in io.readlines()[1:]]: # skip header line
        #    linedata = "%s\t%s\r\n" % (line[0].strip(), line[-1].strip())
        #    #print linedata
        #    f.write(linedata)
        f.close()
        print "Wrote file '%s'" % filename

    def loadFromFile(self, filename):
        data = {}
        try:
            for line in open(filename).readlines():
                if line.find("Date,Open") > -1:
                    continue # skip header
                items = line.strip().split(",")
                date, _open, high, low, unused, volume, _close = items
                _open = float(_open)
                high = float(high)
                low = float(low)
                volume = float(volume)
                _close = float(_close)
                #day = int(date[:2])
                #month = int(date[3:5])
                #year = int(date[6:])
                year = int(date[:4])
                month = int(date[5:7])
                day = int(date[-2:])
                date = datetime.date(year, month, day)
                #data[date] = (_open, high, low, volume, _close)
                yield (date, _open, high, low, _close, volume)
                #print date, date.day, date.weekday()
        except IOError:
            print "Failed to load file '%s'" % filename
        else:
            print "Loaded '%s'" % filename

    def setDateRangeToAll(self):
        self._startdate = self._data[0].date
        self._enddate = self._data[-1].date
        
    def dateToIndex(self, origdate):
        date = origdate
        for i in range(10):
            idx = self._date_to_index.get(date)
            if idx:
                #print "%s (%s) -> %d (%d tries)" % (date, origdate, idx, i+1)
                return idx
            date = date + datetime.timedelta(days=1)
        return None

    def doVerbose(self, verbose):
        if verbose.strip().lower() in ("yes", "on", "1", "true"):
            self.verbose = True
        else:
            self.verbose = False
    
    def doHelp(self):
        print
        print "=" * 80
        print "HELP"
        print "=" * 80
        print
        print "help - displays this help"
        print
        print "path [newpath] - display or set path used to find local price data"
        print
        print "dir - list the local data files in current path"
        print
        print "use <ticker> - work with a price history for <ticker>"
        print
        print "reload - get latest data for current ticker"
        print
        print "drange <daterange> - set default date range"
        print
        print "hist [daterange] - show histogram of price changes for date range"
        print
        print "spot [daterange] - show spot values and histogram for date range"
        print
        print "accum <pct> [daterange] - analyse time taken to accumulate <pct> change"
        print
        print "avgaccum <days> [daterange] - show average pct accumulation over <days> days" 
        print
        #print "plot [daterange] - TODO:"
        #print
        #print "stats [daterange] - show basic stats"
        #print
        #print "hist <n> <m> <sig> [daterange] - show <n>-day histories with at least <m> matches"
        #print "  <sig> means only display patterns that precede an up/down day >= <sig>% of the time"
        #print "  e.g. history 3 20 70 - shows 3 day histories with at least 20 matches"
        #print "       where the number of subsequent up or down days >= 70%"
        #print
        #print "hist <pattern>[*] <m> [sig] [daterange] - find pattern with at least <m> matches"
        #print "  <pattern> is a sequence of U and D characters representing up/down days"
        #print "  <sig> means only display patterns that precede an up/down day >= <sig>% of the time"
        #print "  if pattern is follwed by *, all pattern suffixes are also searched"
        #print "  e.g. find UDUDUU 20 70 - finds UDUDUU pattern with at least 20 matches"
        #print "       where the number of subsequent up or down days >= 70%"
        #print
        print "quit - quits the program"
        print
        print "NOTES:"
        print " daterange -> date[-date] | date[:days] | 'all'"
        print " date -> YYYY | YYYYMM | YYYYMMDD"
        print
        print "=" * 80
        print

    def doPath(self, *args):
        if len(args) == 1:
            path = args[0]
            if os.path.exists(path):
                self._path = path
                print "new path: %s" % self._path
            else:
                print "invalid path '%s'" % path
        else:
            print "current path: %s" % self._path

    def doDir(self):
        files = os.listdir(self._path)
        for file in files:
            if file.endswith("_spot_history.tdf"):
                print file

    def doUse(self, symbol):
        self.load(symbol, os.path.join(self._path, "%s_spot_history.tdf" % symbol))

    def doReload(self):
        filename = os.path.join(self._path, "%s_spot_history.tdf" % self._underlying)
        try:
            os.unlink(filename)
        except:
            pass
        self.load(self._underlying, filename)
        
    def iterData(self, startdate, enddate):
        #print "iterData %s %s" % (startdate, enddate)
        updays = downdays = 0
        uppts = downpts = netpts = 0.0
        #print startdate, self._date_to_index
        startidx = self.dateToIndex(startdate) or 0
        endidx = self.dateToIndex(enddate) or len(self._data)-1
        firstitem = None
        while startidx <= endidx:
            item = self._data[startidx]
            if firstitem is None:
                firstitem = item
            else:
                if item.upday:
                    updays += 1
                    uppts += item.ptschange
                else:
                    downdays += 1
                    downpts += abs(item.ptschange)
            pctchange = (item.close - firstitem.close) / firstitem.close * 100.0  # excludes gain on first date        
            yield (item, firstitem, updays, downdays, uppts, downpts, pctchange) 
            startidx += 1
        
        #firstitem = None
        #for item in self._data:
            #if item.date < startdate:
                #continue
            #elif item.date > enddate:
                #break
            #if firstitem is None:
                #firstitem = item
            #else:
                #if item.upday:
                    #updays += 1
                    #uppts += item.ptschange
                #else:
                    #downdays += 1
                    #downpts += abs(item.ptschange)
            #pctchange = (item.close - firstitem.close) / firstitem.close * 100.0  # excludes gain on first date        
            #yield (item, firstitem, updays, downdays, uppts, downpts, pctchange) 
            
    #def pctChange(self, items):
    #    firstspot = items[0].spot
    #    lastspot = items[-1].spot
    #    pctchange = (lastspot - firstspot) / firstspot * 100.0  # excludes gain on first date
    #    return pctchange

    def doSpot(self):
        return self._spotHelper(doprint=True)
        
    def doHist(self):
        return self._spotHelper(doprint=False)
    
    def _spotHelper(self, doprint):
        changes = []
        for item, firstitem, updays, downdays, uppts, downpts, pctchange in self.iterData(self._startdate, self._enddate):
            changes.append(item.pctchange)
            if doprint:
                print item
        try:
            netpts = uppts - downpts
            print "%d price changes, (%d up, %d down)" % (updays+downdays, updays, downdays)
            print "%.2f pts total change (%.2f pts up, %.2f pts down)" % (netpts, uppts, downpts)
            print "first close: %.2f, last close: %.2f (%.2f%% change)" % (firstitem.close, item.close, pctchange)
            hist = self.histogram(changes, 0.2, labelsuffix="%")
            self.printHistogram(hist)
        except UnboundLocalError:
            # this happens if iterData didn't yield anything (e.g. invalid date range)
            pass
        
    def doAccum(self, pct):
        startdate, enddate = self._startdate, self._enddate
        pct = float(pct)
        print "Checking # of days to accumulate %3.2f%% between %s and %s" % \
                (pct, formatDate(startdate), formatDate(enddate))
        occurrences = []
        i = 0
        while True:
            if (i+1) % 100 == 0:
                print "Looking at prices starting from %s..." % startdate
            for item, firstitem, updays, downdays, uppts, downpts, pctchange in self.iterData(startdate, enddate):
                if (pct >= 0 and pctchange >= pct) or (pct < 0 and pctchange <= pct):
                    i = 0
                    if self.verbose:
                        print "Accumulated %.2f%% between %s and %s (%d days)" % (pctchange, firstitem.date, item.date, (updays+downdays))
                    occurrences.append([updays+downdays, (firstitem.date, item.date, pctchange)])
                    break
            i += 1
            #print "startdate was %s" % startdate
            startdate = firstitem.date + datetime.timedelta(days=1)
            #print "startdate now %s" % startdate
            if startdate >= enddate:
                break
            
        if len(occurrences) == 0:
            print "never accumulated %3.2f%% pct between %s and %s" % (pct, self._startdate, self._enddate)
        else:
            print "accumulated %3.2f%% pct %d times" % (pct, len(occurrences))
            print "min #days: %d, max #days: %d, avg #days: %.1f" % (min([x[0] for x in occurrences]),
                                                                     max([x[0] for x in occurrences]),
                                                                     float(sum([x[0] for x in occurrences]))/len(occurrences))
            print "top 10 fastest accumulations:"
            occurrences.sort()
            for numdays, (firstdate, lastdate, pctchange) in occurrences[:10]:
                print " %3.2f%% from %s to %s (%d days)" % (pctchange, firstdate, lastdate, numdays)
            print "top 10 slowest accumulations:"
            occurrences = occurrences[::-1]
            for numdays, (firstdate, lastdate, pctchange) in occurrences[:10]:
                print " %3.2f%% from %s to %s (%d days)" % (pctchange, firstdate, lastdate, numdays)
            hist = self.histogram([x[0] for x in occurrences], 10, labelsuffix=" days", minbucket=0)
            self.printHistogram(hist)
        

    def doAvgAccum(self, numdays):
        startdate, enddate = self._startdate, self._enddate
        numdays = int(numdays)
        print "Checking average accumulation over %d days between %s and %s" % \
                (numdays, formatDate(startdate), formatDate(enddate))
        occurrences = []
        while True:
            for item, firstitem, updays, downdays, uppts, downpts, pctchange in self.iterData(startdate, enddate):
                if (updays + downdays == numdays):
                    if self.verbose:
                        print "Accumulated %.2f%% between %s and %s (%d days)" % (pctchange, firstitem.date, item.date, numdays)
                    occurrences.append([pctchange, firstitem.date, item.date])
                    break
            startdate = firstitem.date + datetime.timedelta(days=1)
            if startdate >= enddate:
                break
        occurrences.sort()
        if len(occurrences) == 0:
            print "no time period of %d days between %s and %s" % (numdays, self._startdate, self._enddate)
        else:
            # TODO: histogram so we know how common it is to go up/down X% ac
            print "%d occurrences of %d day sequence" % (len(occurrences), numdays)
            print "min pct change: %.2f%% between %s and %s" % (occurrences[0][0], occurrences[0][1], occurrences[0][2])
            print "max pct change: %.2f%% between %s and %s" % (occurrences[-1][0], occurrences[-1][1], occurrences[-1][2])
            print "avg pct change: %.2f%%" % (float(sum([x[0] for x in occurrences]))/len(occurrences))
            hist = self.histogram([x[0] for x in occurrences], 2, labelsuffix="%")
            self.printHistogram(hist)

    def histogram(self, values, bucketsize, labelsuffix="", minbucket=None, maxbucket=None):
        numvalues = len(values)
        values.sort()
        minvalue, maxvalue = values[0], values[-1]
        results = []
        if minbucket is None:
            if abs(minvalue) > abs(maxvalue):
                # minvalue must be negative
                minbucket = minvalue
            else:
                minbucket = -maxvalue
        if maxbucket is None:
            if abs(minvalue) > abs(maxvalue):
                # minvalue must be negative
                maxbucket = -minvalue
            else:
                maxbucket = maxvalue
        minbucket = int(round(minbucket))
        maxbucket = int(round(maxbucket))
        if bucketsize == int(bucketsize):
            buckets = range(minbucket, maxbucket+bucketsize, bucketsize)
        else:
            buckets = [x/100.0 for x in range(minbucket*100, maxbucket*100+int(round(bucketsize*100)), 
                                              int(round(bucketsize*100)))]
        #bucketsize = int(round(bucketsize)) or 1
        #buckets = range(minbucket, maxbucket+bucketsize, bucketsize)
        buckets.append(buckets[-1])
        #print minbucket, maxbucket, buckets
        for i, bucket in enumerate(buckets):
            if i==0:
                fn = lambda x : x < bucket
                label = "< %5.1f%s" % (bucket, labelsuffix)
            elif i==len(buckets)-1:
                fn = lambda x : x >= bucket
                label = ">= %5.1f%s" % (bucket, labelsuffix)
            else:
                fn = lambda x : buckets[i-1] <= x < bucket
                label = "%5.1f%s to <%5.1f%s" % (buckets[i-1], labelsuffix, bucket, labelsuffix)
            count = 0
            for value in values:
                if fn(value):
                    count += 1
            results.append([label, float(count), numvalues])
        return results

    def printHistogram(self, hist):
        maxcount = max([x[1] for x in hist])
        maxlabel = max([len(x[0]) for x in hist])
        maxpct = max([count/total for label, count, total in hist])
        numstars = 100.0 / maxpct
        digits = int(round(math.log(maxcount)))
        #print "max is %d" % maxcount
        format = "%%s: %%%dd (%%4.1f%%%%, %%5.1f%%%%) %%s" % digits
        #print "format=>>%s<<"% format
        totalpct = 0.0
        for label, count, total in hist:
            if len(label) < maxlabel:
                label = (" " * (maxlabel-len(label))) + label
            thispct = count/total*100.0
            totalpct += thispct
            stars = ("*"*int(round(count/total*numstars)))
            if count and not stars:
                # so at least a 'miniature asterisk' prints when count is nonzero...
                stars = "."
            print format % (label, count, thispct, totalpct, stars)
            
    """        
    def doSpot(self, args):
        origstartdate, origenddate = self._startdate, self._enddate
        numdays = 9999999
        try:
            if len(args) == 2:
                # temporarily override dates
                if args[1] == "all":
                    self.setDateRangeToAll()
                else:
                    try:
                        numdays = int(args[1])
                    except (ValueError, TypeError):
                        startdate, enddate = self.parseDateRange(args[1])
                        if (startdate is None) or (enddate is None):
                            return self.doHelp()
                        self._startdate, self._enddate = startdate, enddate
                    else:
                        self._enddate = datetime.date.today()
                        self._startdate = self._enddate - datetime.timedelta(days=numdays)
                    print "Printing spot between %s and %s" % (formatDate(self._startdate), formatDate(self._enddate))
            elif len(args) == 3:
                startdate = self.parseDate(args[1], True)
                if startdate is None:
                    return self.doHelp()
                enddate = datetime.date(9999,1,1)
                self._startdate, self._enddate = startdate, enddate
                numdays = int(args[2])
                print "Printing %d days of spot starting %s" % (numdays, formatDate(self._startdate))
            ndays = updays = downdays = 0
            uppts = downpts = netpts = 0.0
            firstspot = lastspot = None
            for i, item in enumerate(self._data):
                if item.date < self._startdate:
                    continue
                elif item.date > self._enddate:
                    break
                elif numdays <= 0:
                    break
                lastspot = item.spot
                if firstspot is None:
                    firstspot = item.spot
                else:
                    ndays += 1
                    if item.upday:
                        updays += 1
                        uppts += item.ptschange
                    else:
                        downdays += 1
                        downpts += abs(item.ptschange)
                print item
                numdays -= 1
            netpts = uppts - downpts
            pctchange = (lastspot - firstspot) / firstspot * 100.0  # excludes gain on first date
            #pctchange = netpts / firstspot * 100.0 # includes gain on 1st date
            print "%d price changes, (%d up, %d down)" % (ndays, updays, downdays)
            print "%.2f pts total change (%.2f pts up, %.2f pts down)" % (netpts, uppts, downpts)
            print "first spot: %.2f, last spot: %.2f (%.2f%% change)" % (firstspot, lastspot, pctchange)
        finally:
            self._startdate, self._enddate = origstartdate, origenddate
    """

    """            
    def doAccum(self, args):
        # arg[1] - points
        # optional arg[2] - daterange
        origstartdate, origenddate = self._startdate, self._enddate
        try:
            if len(args) == 3:
                points = float(args[1])
                # temporarily override dates
                if args[2] == "all":
                    self.setDateRangeToAll()
                else:
                    startdate, enddate = self.parseDateRange(args[2])
                    if (startdate is None) or (enddate is None):
                        return self.doHelp()
                    self._startdate, self._enddate = startdate, enddate
            elif len(args) == 2:
                points = float(args[1])
            else:
                return self.doHelp()
            print "Checking # of days to accumulate %3.2f points" % points 
            print "Using date range %s to %s" % (formatDate(self._startdate), formatDate(self._enddate))

            mindays = 9999999
            maxdays = 0
            totaldays = 0
            numtrials = 0
            occurrences= []

            for i, startitem in enumerate(self._data):
                if startitem.date < self._startdate:
                    continue
                elif startitem.date > self._enddate:
                    break
                accum = 0.0
                numdays = 0
                j = i+1
                while j < len(self._data):
                    enditem = self._data[j]
                    if enditem.date > self._enddate:
                        break
                    #print "d1: %s, d2: %s" % (startitem.date, enditem.date)
                    numdays += 1
                    accum += enditem.ptschange
                    #print "accum=%3.2f" % accum
                    if (points > 0 and accum >= points) or (points < 0 and accum <= points):
                        print "accumulated %3.2f points between %s and %s (%d days)" % (accum, startitem.date, enditem.date, numdays)
                        if numdays < mindays:
                            mindays = numdays
                            mindates = "%s and %s" % (startitem.date, enditem.date)
                        if numdays > maxdays:
                            maxdays = numdays
                        totaldays += numdays
                        numtrials += 1
                        occurrences.append([numdays, (startitem.date, enditem.date, accum)])
                        break 
                    j += 1
            if numtrials == 0:
                print "never accumulated %3.2f points between %s and %s" % (points, self._startdate, self._enddate)
            else:
                print "accumulated %3.2f points %d times" % (points, numtrials)
                print "min #days: %d, max #days: %d, avg #days: %.1f" % (mindays, maxdays, float(totaldays)/float(numtrials))
                print "top 10 fastest accumulations:"
                occurrences.sort()
                for numdays, o in occurrences[:10]:
                    print " from %s to %s (%d days): %3.2f points" % (o[0], o[1], numdays, o[2])
                print "top 10 slowest accumulations:"
                occurrences = occurrences[::-1]
                for numdays, o in occurrences[:10]:
                    print " from %s to %s (%d days): %3.2f points" % (o[0], o[1], numdays, o[2])

        finally:
            self._startdate, self._enddate = origstartdate, origenddate
    """
    """
    def doAvgAccum(self, args):
        # arg[1] - numdays
        # optional arg[2] - daterange
        origstartdate, origenddate = self._startdate, self._enddate
        try:
            if len(args) == 3:
                numdays = float(args[1])
                # temporarily override dates
                if args[2] == "all":
                    self.setDateRangeToAll()
                else:
                    startdate, enddate = self.parseDateRange(args[2])
                    if (startdate is None) or (enddate is None):
                        return self.doHelp()
                    self._startdate, self._enddate = startdate, enddate
            elif len(args) == 2:
                numdays = float(args[1])
            else:
                return self.doHelp()
            print "Checking average accumulation over %d days" % numdays 
            print "Using date range %s to %s" % (formatDate(self._startdate), formatDate(self._enddate))

            minpoints = 9999999
            maxpoints = 0
            mindate = None
            maxdate = None
            totalpoints = 0
            numtrials = 0
            #occurrences= []

            for i, startitem in enumerate(self._data):
                if startitem.date < self._startdate:
                    continue
                elif startitem.date > self._enddate:
                    break
                accum = 0.0
                days = 0
                j = i+1
                while j < len(self._data):
                    enditem = self._data[j]
                    if enditem.date > self._enddate:
                        break
                    #print "d1: %s, d2: %s" % (startitem.date, enditem.date)
                    days += 1
                    accum += enditem.ptschange
                    #print "accum=%3.2f" % accum
                    if (days >= numdays):
                        print "accumulated %3.2f points between %s and %s (%d days)" % (accum, startitem.date, enditem.date, numdays)
                        if accum < minpoints:
                            minpoints = accum
                            mindate = startitem.date
                        if accum > maxpoints:
                            maxpoints = accum
                            maxdate = startitem.date
                        totalpoints += accum
                        numtrials += 1
                        #occurrences.append([numdays, (startitem.date, enditem.date, accum)])
                        break 
                    j += 1
            if numtrials == 0:
                print "no data"
            else:
                print "%d occurrences of %d day sequence" % (numtrials, numdays)
                print "min points: %.2f starting on %s" % (minpoints, mindate)
                print "max points: %.2f starting on %s" % (maxpoints, maxdate)
                print "avg points: %.2f" % (float(totalpoints)/float(numtrials))
        finally:
            self._startdate, self._enddate = origstartdate, origenddate
    """
    
    """
    # TODO: mostly copied and pasted--lame
    def doDist(self, args):
        import decimal
        origstartdate, origenddate = self._startdate, self._enddate
        numdays = 9999999
        try:
            if len(args) == 2:
                # temporarily override dates
                if args[1] == "all":
                    self.setDateRangeToAll()
                else:
                    try:
                        numdays = int(args[1])
                    except (ValueError, TypeError):
                        startdate, enddate = self.parseDateRange(args[1])
                        if (startdate is None) or (enddate is None):
                            return self.doHelp()
                        self._startdate, self._enddate = startdate, enddate
                    else:
                        self._enddate = datetime.date.today()
                        self._startdate = self._enddate - datetime.timedelta(days=numdays)
                    print "Calculating spot price distribution between %s and %s" % (formatDate(self._startdate), formatDate(self._enddate))
            elif len(args) == 3:
                startdate = self.parseDate(args[1], True)
                if startdate is None:
                    return self.doHelp()
                enddate = datetime.date(9999,1,1)
                self._startdate, self._enddate = startdate, enddate
                numdays = int(args[2])
                print "Calculating %d days of spot price distribution starting %s" % (numdays, formatDate(self._startdate))
            diffs = {}
            roundTo = 0.25
            numSamples = 0
            for i, item in enumerate(self._data):
                if item.date < self._startdate:
                    continue
                elif item.date > self._enddate:
                    break
                elif numdays <= 0:
                    break
                numSamples += 1
                #print "%d - %s: %3.2f" % (numSamples, item.date, item.pctchange)
                diff = int(item.pctchange / roundTo) * roundTo
                diff = decimal.Decimal(str(diff))
                diffs[diff] = diffs.get(diff,0) + 1
                numdays -= 1
            for key in diffs.keys():
                # express count as a percentage of total samples
                diffs[key] = (float(diffs[key]) / numSamples) * 100.0
            # so that we can compare distributions year on year more easily, fill in any gaps from -MINMAX to MINMAX
            MINMAX = 8
            x = decimal.Decimal("-%s.0" % MINMAX)
            while x <= decimal.Decimal("%s.0" % MINMAX):
                if not diffs.has_key(x):
                    diffs[x] = "" #0.0
                x = x + decimal.Decimal(str(roundTo))
            keys = diffs.keys()
            keys.sort()
            total = 0.0
            for key in keys:
                print "%s,%s" % (key, diffs[key])
                total += (diffs[key] or 0.0)
            print total
            fp = open(r"c:\temp\dist.xls", "wu")
            for key in keys:
                fp.write("%s\t%s\n" % (key, diffs[key]))
            fp.close()
        finally:
            self._startdate, self._enddate = origstartdate, origenddate
    """

    """
    # Returns a list of (bucket, count). Bucket [-]x holds the number of
    # spot changes between the specified dates that resulted in a change of [-]x% in price.
    # If countInPercent == True then the count is instead returned as a percentage.
    # You can chart this using an X,Y plot in Excel to view the probability distribution
    # of the underlying market.
    def _getDistribution(self, startdate, enddate, countInPercent=False, roundTo=0.5):
        diffs = {}
        #print startdate, enddate
        rows = self._db.execute("select distinct dt, spot from quote where dt between '%s' and '%s' order by dt;" % \
                                (startdate, enddate))
        for i in range(len(rows)-1):
            # NOTE: diff is expressed as a percentage change from previous value
            diff = ((rows[i+1]["spot"] - rows[i]["spot"]) / rows[i]["spot"]) * 100.0
            diff = int(diff / roundTo) * roundTo
            diff = decimal.Decimal(str(diff))
            diffs[diff] = diffs.get(diff,0) + 1
        if countInPercent:
            for key in diffs.keys():
                # express count as a percentage of total samples
                diffs[key] = (float(diffs[key]) / len(rows)) * 100.0
        # so that we can compare distributions year on year more easily, fill in any gaps from -MINMAX to MINMAX
        MINMAX = 8
        x = decimal.Decimal("-%s.0" % MINMAX)
        while x <= decimal.Decimal("%s.0" % MINMAX):
            if not diffs.has_key(x):
                diffs[x] = 0.0
            x = x + decimal.Decimal(str(roundTo))
        keys = diffs.keys()
        keys.sort()
        retval = [(key, diffs[key]) for key in keys]
        return retval
    """

    """
    def doPlot(self, args):
        axesBG  = '#f6f6f6'  # the axis background color
        left, width = 0.1, 0.8
        rect1 = [left, 0.7, width, 0.2]
        axis = axes(rect1, axisbg=axesBG)  #left, bottom, width, height
        copydata = self._data[-30:-1]
        data = []
        for row in copydata:
            data.append((date2num(row.date), row.spot-4, row.spot, row.spot+3, row.spot-5))
        candlestick(axis, data)
        show()
    """

    """
    def doFind(self, args):
        origstartdate, origenddate = self._startdate, self._enddate
        try:
            if len(args) == 5:
                # temporarily override dates
                if args[4] == "all":
                    return self.setDateRangeToAll()
                startdate, enddate = self.parseDateRange(args[4])
                if (startdate is None) or (enddate is None):
                    return self.doHelp()
                self._startdate, self._enddate = startdate, enddate
            try:
                pattern = args[1].upper()
                minpctmatches = float(args[2])
                sig = int(args[3])
            except:
                return self.doHelp()
            allDataByPattern = {}
            tryAllSuffixes = False
            if pattern.endswith("*"):
                tryAllSuffixes = True
                pattern = pattern[:-1]
            while len(pattern) >= 1:
                print "Trying pattern %s" % pattern
                dataByPattern, totaldays = self.doHistoryHelper(len(pattern))
                for key in dataByPattern.keys():
                    if key.startswith(pattern):
                        allDataByPattern[key] = dataByPattern[key]
                if not tryAllSuffixes:
                    break
                pattern = pattern[1:]
            print "Patterns found between %s and %s (%d days):" % (formatDate(self._startdate), formatDate(self._enddate), totaldays)
            self.printDataByPattern(allDataByPattern, totaldays, minpctmatches, sig)
        finally:
            self._startdate, self._enddate = origstartdate, origenddate
    """

    """
    def doHistory(self, args):
        origstartdate, origenddate = self._startdate, self._enddate
        try:
            if len(args) == 5:
                # temporarily override dates
                if args[4] == "all":
                    return self.setDateRangeToAll()
                startdate, enddate = self.parseDateRange(args[4])
                if (startdate is None) or (enddate is None):
                    return self.doHelp()
                self._startdate, self._enddate = startdate, enddate
            try:
                ndays = int(args[1])
                minpctmatches = float(args[2])
                sig = int(args[3])
            except:
                return self.doHelp()
            dataByPattern, totaldays = self.doHistoryHelper(ndays)
            print "Patterns found between %s and %s (%d days):" % (formatDate(self._startdate), formatDate(self._enddate), totaldays)
            self.printDataByPattern(dataByPattern, totaldays, minpctmatches, sig)
        finally:
            self._startdate, self._enddate = origstartdate, origenddate

    def doHistoryHelper(self, ndays):
        dataByPattern = {}
        totaldays = 0
        for i in range(ndays, len(self._data)):
            item = self._data[i]
            date = item.date
            if date < self._startdate:
                continue
            if date > self._enddate:
                break
            totaldays += 1
            lastDayOfMonth = (date + datetime.timedelta(days=1)).month != date.month
            history = []
            #uptotal = downtotal = 0.0
            for j in range(ndays, 0, -1):
                backindex = i-j
                assert (backindex >= 0) # should always be true since we start at index ndays
                upday = self._data[backindex].upday
                if upday:
                    history.append("U")
                    assert self._data[backindex].ptschange >= 0
                    #uptotal += self._data[backindex].ptschange
                else:
                    history.append("D")
                    assert self._data[backindex].ptschange <= 0
                    #downtotal += self._data[backindex].ptschange
            history = "".join(history)
            patterns = []
            if history:
                # user could have asked for 0 history
                patterns.append(history)
                history = history + "-"
            patterns.append("%s%s" % (history, MONTH[date.month]))
            if date.day < 31:
                # don't add this pattern if date is 31st, because 31st is same as 31-EOM
                patterns.append("%s%02d" % (history, date.day))
            patterns.append("%s%s" % (history, DOW[date.weekday()]))
            patterns.append("%s%s-%s" % (history, date.day, DOW[date.weekday()]))
            patterns.append("%s%s-%s" % (history, MONTH[date.month], date.year))
            patterns.append("%s%s" % (history, date.year))
            if dateInOptionExpirationWeek(date):
                patterns.append("%sXPW" % history)
                patterns.append("%s%s-XPW" % (history, MONTH[date.month]))
                patterns.append("%s%02d-XPW" % (history, date.day))
                patterns.append("%s%s-XPW" % (history, DOW[date.weekday()]))
                patterns.append("%s%s-%s-XPW" % (history, MONTH[date.month], date.year))
                patterns.append("%s%s-XPW" % (history, date.year))
            if lastDayOfMonth:
                patterns.append("%sEOM" % history)
                patterns.append("%s%s-EOM" % (history, MONTH[date.month]))
                patterns.append("%s%02d-EOM" % (history, date.day))
                patterns.append("%s%s-EOM" % (history, DOW[date.weekday()]))
                patterns.append("%s%s-%s" % (history, date.day, DOW[date.weekday()]))
                patterns.append("%s%s-%s-EOM" % (history, MONTH[date.month], date.year))
                patterns.append("%s%s-EOM" % (history, date.year))
                # I don't think it's possible for the last day of the month to occur during
                # expiration week, so don't bother adding those patterns
            for pattern in patterns:
                counts = dataByPattern.get(pattern, [0.0, 0.0, None, None, 0.0])  # updays, downdays, minpts, maxpts, ptschange
                if item.upday:
                    # current day is an up day
                    counts[0] += 1
                else:
                    counts[1] += 1
                if (counts[2] is None) or (item.ptschange < counts[2]):
                    counts[2] = item.ptschange
                if (counts[3] is None) or (item.ptschange > counts[3]):
                    counts[3] = item.ptschange
                counts[4] += item.ptschange
                dataByPattern[pattern] = counts
        return dataByPattern, totaldays
    """
    
    """
    def printDataByPattern(self, dataByPattern, totaldays, minpctmatches, sig):
        keys = dataByPattern.keys()
        keys.sort()
        lastprinted = None
        for key in keys:
            updays, downdays, minpts, maxpts, ptschange = dataByPattern[key]
            uppct = (updays/float(updays+downdays)*100.0)
            downpct = (downdays/float(updays+downdays)*100.0)
            avgpts = ptschange/(updays+downdays)
            pctmatched = (float(updays)+downdays)/totaldays*100.0
            if minpctmatches == 0 and ((updays+downdays) < 2):
                # even if minpctmatches is zero (i.e. user is trying to see all patterns regardless
                # of how often they occurred), don't show a pattern that was only matched once. There can't
                # be any value in showing a pattern that only happened once.
                continue
            if (pctmatched > minpctmatches) and (uppct > sig or downpct > sig):
                # mark especially good matches with a star
                space = ""
                if lastprinted and key.startswith(lastprinted):
                    space = " "
                if (uppct > sig and minpts > 0) or (downpct > sig and maxpts < 0):
                    mark = "*"
                elif (uppct > sig and avgpts < 0) or (downpct > sig and avgpts > 0):
                    mark = "?"
                else:
                    mark = ""
                print "%s%s%s led to %s up days (%3.2f%%), %s down days (%3.2f%%), %.2f min/%.2f max/%.2f avg pts" % \
                      (space, mark, key, updays, uppct, downdays, downpct, minpts, maxpts, avgpts)
                lastprinted = key
    """

    def doDateRange(self, daterange):
        if daterange == "all":
            return self.setDateRangeToAll()
        self._startdate, self._enddate = self.parseDateRange(daterange)

    def parseDateRange(self, daterange):
        # check for colon must come before check for dash as we might have yyyymmdd:-nn or some such
        if daterange.find(":") > -1:
            startdate, numdays = daterange.split(":")
            startdate = self.parseDate(startdate, True)
            numdays = int(numdays) # TODO: trap error
            enddate = startdate + datetime.timedelta(days=numdays)
            # numdays could be negative, so need the min/max below
            startdate, enddate = min(startdate, enddate), max(startdate, enddate)
        elif daterange.find("-") > -1:
            startdate, enddate = daterange.split("-")
            startdate, enddate = self.parseDate(startdate, True), self.parseDate(enddate, False)
        else:
            startdate, enddate  = self.parseDate(daterange, True), self.parseDate(daterange, False)
        #print "parseDateRange returns %s, %s" % (startdate, enddate)
        return startdate, enddate

    def parseDate(self, strdate, isStartDate):
        try:
            if (strdate.lower() in ["today"]):
                date = datetime.date.today()
            elif len(strdate) == 4:
                # YYYY
                date = datetime.date(int(strdate), 1, 1)
            elif len(strdate) == 6:
                # YYYYMM
                date = datetime.date(int(strdate[:4]), int(strdate[4:]), 1)
            elif len(strdate) == 8:
                # YYYYMMDD
                date = datetime.date(int(strdate[:4]), int(strdate[4:6]), int(strdate[6:]))
            elif len(strdate) == 10:
                # YYYY-MM-DD
                date = datetime.date(int(strdate[:4]), int(strdate[5:7]), int(strdate[-2:]))
            else:
                raise ValueError
        except Exception:
            if isStartDate:
                return self._data[0].date
            else:
                return self._data[-1].date
        if len(strdate) == 4 and (not isStartDate):
            date = datetime.date(date.year, 12, 31)
        elif len(strdate) == 6 and (not isStartDate):
            for lastday in range(31, 27, -1):
                try:
                    date = datetime.date(date.year, date.month, lastday)
                except ValueError:
                    pass
                else:
                    break
        if isStartDate and (date < self._data[0].date):
            print "Warning: specified start date is before beginning of history (%s)" % self._data[0].date
            date = self._data[0].date
        if (not isStartDate) and (date > self._data[-1].date):
            print "Warning: specified end date is after end of history (%s)" % self._data[-1].date
            date = self._data[-1].date
        return date

    def prompt(self):
        if self._underlying is None:
            return "No data loaded. type 'use <symbol>' to load data, or 'help' for help\n>"
        else:
            return "%s %s-%s>" % (self._underlying, formatDate(self._startdate), formatDate(self._enddate))
        
    def doQuit(self):
        if self._underlying:
            # save name of last underlying we used
            open(os.path.join(self._path, "analyze_prices.last"), "wu").write(self._underlying)
        sys.exit(0)

    def run(self):
        COMMANDS = {"help"       : (self.doHelp,     0, 0, False),
                    "quit"       : (self.doQuit,     0, 0, False),
                    "bye"        : (self.doQuit,     0, 0, False),
                    "dir"        : (self.doDir,      0, 0, False),
                    "use"        : (self.doUse,      1, 1, False), 
                    "load"       : (self.doUse,      1, 1, False),
                    "reload"     : (self.doReload,   0, 0, False),
                    "path"       : (self.doPath,     0, 1, False),
                    "spot"       : (self.doSpot,     0, 1, True),
                    "hist"       : (self.doHist,     0, 1, True),
                    "drange"     : (self.doDateRange,1, 1, False),
                    "daterange"  : (self.doDateRange,1, 1, False),
                    "dates"      : (self.doDateRange,1, 1, False),
                    "accum"      : (self.doAccum,    1, 2, True),
                    "avgaccum"   : (self.doAvgAccum, 1, 2, True),
                    "verbose"    : (self.doVerbose,  1, 1, False),
                    }
                    
        print "analyze_prices (c) 2007-2008 kevin.manley@gmail.com"
        try:
            # try to restore state of last underlying from last session
            underlying = open(os.path.join(self._path, "analyze_prices.last"), "ru").read()
        except:
            pass
        else:
            self.doUse(underlying)
        while True:
            try:
                args = [arg.lower().strip() for arg in raw_input(self.prompt()).split()]
                try:
                    key = args[0]
                    cmd = COMMANDS[key]
                except (KeyError,IndexError):
                    if args:
                        print "Sorry I didn't understand that command. Try 'help' for help"
                    continue
                fn, minargs, maxargs, optionalDateRange = cmd
                args = args[1:]
                if not minargs <= len(args) <= maxargs:
                    if minargs==maxargs:
                        if minargs == 0:
                            print "%s expects no args. Try 'help' for help" % (key, minargs)
                        else:
                            print "%s expects %d arg. Try 'help' for help" % (key, minargs)
                    else:
                        print "%s expects between %d and %d args. Try 'help' for help" % (key, minargs, maxargs)
                    continue
                try:
                    origstartdate, origenddate = self._startdate, self._enddate
                    if optionalDateRange and len(args) == maxargs:
                        self.doDateRange(args[-1])
                        args = args[:-1] # remove daterange from list of args passed to function
                    start = time.clock()
                    fn(*args)
                finally:
                    elapsed = (time.clock() - start) * 1000.0
                    print "Elapsed: %.2f msecs" % elapsed
                    if fn != self.doDateRange:
                        self._startdate, self._enddate = origstartdate, origenddate
                                
                
                #if cmd=="help":
                #    self.doHelp()
                #    continue
                #elif cmd=="quit" or cmd=="bye":
                #    if self._underlying:
                #        # save name of last underlying we used
                #        open(os.path.join(self._path, "analyze_prices.last"), "wu").write(self._underlying)
                #    break
                #elif cmd=="dir":
                #    self.doDir(args)
                #    continue
                #elif cmd=="use" or cmd=="load":
                #    self.doUse(args)
                #    continue
                #elif cmd=="reload":
                #    self.doReload(args)
                #    continue
                #elif cmd=="path":
                #    self.doPath(args)
                #    continue
                #else:
                #    print "Sorry, I didn't understand. You can type 'help' to get help"
                # the following commands are only valid if we have loaded data
                
                """
                if self._underlying:
                    if cmd=="drange" or cmd=="daterange" or cmd=="dr":
                        self.doDateRange(args)
                    elif cmd=="spot":
                        self.doSpot(args)
                    elif cmd=="accum":
                        self.doAccum(args)
                    elif cmd=="avgaccum":
                        self.doAvgAccum(args)
                    elif cmd=="dist":
                        self.doDist(args)
                    elif cmd=="plot":
                        self.doPlot(args)
                    elif cmd.startswith("hist"):
                        if len(args) > 1:
                            try:
                                int(args[1])
                            except ValueError:
                                # not an int, must be UD pattern
                                self.doFind(args)
                            else:
                                self.doHistory(args)
                    else:
                        print "Sorry, I didn't understand. You can type 'help' to get help"
                """
            except KeyboardInterrupt:
                print

"""
for i in range(1, len(data)):
    if not (startdate <= data[i][0] <= enddate):
        continue
    if data[i][1] > data[i-1][1]:
        data[i][2] = True # mark as an up day
        weekday = data[i][0].weekday()
        upDaysByWeekday[weekday] = upDaysByWeekday.get(weekday, 0) + 1
        day = data[i][0].day
        upDaysByDay[day] = upDaysByDay.get(day, 0) + 1

print "up days by weekday:"
keys = upDaysByWeekday.keys()
keys.sort()
for key in keys:
    print "%s,%s" % (key, upDaysByWeekday[key])

print "up days by day:"
keys = upDaysByDay.keys()
keys.sort()
for key in keys:
    print "%s,%s" % (key, upDaysByDay[key])
"""

if __name__ == "__main__":
    p = PriceAnalyzer()
    #result = p.histogram([-20, -20, -10, -1, 0, 5, 6, 7, 8, 9, 10, 20, 100], 5, labelsuffix="%")
    #p.printHistogram(result)
    #for label, count, total in result:
    #    print label, "*"*int(count/total*80)
    #sys.exit(0)
    
    
    #date = datetime.date.today()
    #for i in range(60):
    #    print date, dateInOptionExpirationWeek(date)
    #    date = date + datetime.timedelta(days=1)
    #sys.exit(0)
    #p = PriceAnalyzer()
    #p.load("RUT", r"c:\bot\rut_spot_history.tdf")
    #pprint.pprint(p._data)
    p.run()
