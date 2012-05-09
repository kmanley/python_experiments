import re
import argparse
import urlparse
import http
import logging
log = logging.getLogger()
import licensed_code.veltro.utils.xmltools as xmltools

class SvnCrawler(object):
    def __init__(self, *args, **kwargs):
        self.http = http.HTTPClient(*args, **kwargs)
        self.queue = []

    def _crawl_queue(self):
        url = self.queue.pop(0)
        log.info("getting %s (qlen=%d)" % (url, len(self.queue)))
        try:
            data = self.http.get(url)
        except http.Error, e:
            if e.httpcode == 403:
                log.warning("access denied for %s; skipping it..." % url)
                return 
            else:
                raise
            
        if data.find('<svn version=') > -1:
            root = xmltools.ElementTreeParse(data).getroot()
            #print xmltools.ElementTreeToString(root)         
            index = root[0]
            for elem in index:
                if elem.tag in ("file", "dir"):
                    new_url = url + elem.get("href")
                    if self.should_crawl(new_url):
                        self.queue.append(new_url)
                        log.info("enqueued %s (qlen=%d)" % (new_url, len(self.queue)))
                    else:
                        log.info("skipping %s" % new_url)
        else:
            self.process_file(url, data)
        
    def crawl(self, url):
        if not url.endswith("/"):
            url = url + "/"
        self.queue.append(url)
        while self.queue:
            self._crawl_queue()
            
    def should_crawl(self, url):
        return True
        
    def process_file(self, data):
        pass 
    
class StdCrawler(SvnCrawler):
    def __init__(self, regex, *args, **kwargs):
        kwargs.setdefault("verify_ssl_cert", False)
        SvnCrawler.__init__(self, *args, **kwargs)
        self.regex = re.compile(regex, re.IGNORECASE)
        self.fp = open("crawler_result.txt", "w")
        
    def should_crawl(self, url):
        NOCRAWL = ("/tag", "/branch", "/release", "/releasetags")
        for item in NOCRAWL:
            if item.lower() in url.lower():
                return False
        return True
    
    def process_file(self, url, data):
        log.info("processing %s (%d bytes)" % (url, len(data)))
        if re.search(self.regex, data):
            self.fp.write(url + "\r\n")
            self.fp.flush()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SVN crawler")
    parser.add_argument("start_url", type=str, help="starting URL")
    parser.add_argument("regex", type=str, help="regex to search for")
    args = parser.parse_args()
    crawler = StdCrawler(args.regex)
    crawler.crawl(args.start_url)
    
    
