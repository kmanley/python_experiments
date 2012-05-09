#!/usr/bin/env python
 
from BeautifulSoup import BeautifulSoup
from http import HTTPClient
#import urllib2
#import random
#import re
#import sqlite3
import logging
 
#DATABASE   = ':memory:'
LOG_LEVEL  = logging.INFO
ABS_URL_RE = re.compile('(?P<url>https?://.+?/)')
 
class WebCrawler:
    def __init__(self, logging_level=LOG_LEVEL):
        logging.basicConfig(level=logging_level)
        #self.conn = sqlite3.connect(database)
        #self.conn.execute('create table url_stack (url text)')
        #self.conn.execute('create table url_visited (url text)')
 
    def _form_url(self, url, link):
        if link[0:4] == 'http':
            ret_url = link
        elif link[0] == '/':
            m = ABS_URL_RE.search(url)
            ret_url = "%s%s" % (m.group('url'), link[1:])
        else:
            ret_url = "%s%s" % (url, link)
        return ret_url
 
    def _pop_from_db(self):
        logging.debug("Retrieving one URL from the DB...")
        res = self.conn.execute('select url from url_stack limit 1').fetchone()
        logging.debug("Query result: %s", res)
        url = res[0]
        self.conn.execute("delete from url_stack where url = ?", (url,))
        return url
 
    def _push_to_db(self, url):
        logging.debug("Inserting record into DB...")
        logging.debug("Check if it hasn't been visited yet")
        if not self.conn.execute('select url from url_visited where url=?', (url,)).fetchone():
            logging.debug("URL not found in list of visited URLs, inserting")
            logging.debug("URL to insert: %s" % url)
            self.conn.execute('insert into url_stack values (?)', (url,))
            self.conn.execute('insert into url_visited values (?)', (url,))
        else:
            logging.debug("URL has already been visited or added for processing, skipping")
 
    def crawl(self, url):
        work_url = url
        logging.debug("Work URL: %s" % work_url)
        while True:
            try:
                logging.debug("Trying to open and parse the URL...")
                page = urllib2.urlopen(work_url)
                soup = BeautifulSoup(page)
                logging.debug("Parsed successfuly")
            except:
                logging.debug("Failed to parse, attempting to get next URL from DB")
                work_url = self._pop_from_db()
                continue
            links = soup('a')
            logging.debug("Found total of %d links (<a href=...>)" % len(links))
            for link in soup('a'):
                logging.debug("Processing link object: %s" % link)
                try:
                    if link['href'] != '':
                        self._push_to_db(self._form_url(work_url, link['href']))
                except:
                    logging.debug("An exception has occured, this may be ok (href attribute may be missing)")
                    logging.debug("  ... but can also indicate error in insert code")
            logging.debug("Finished adding URLs")
            logging.debug("Getting a new URL for processing from DB")
            work_url = self._pop_from_db()
            logging.info("Found URL: %s" % work_url)
            yield work_url
 
if __name__ == '__main__':
    wc = WebCrawler()
    for url in wc.crawl('http://www.google.com/'):
        pass