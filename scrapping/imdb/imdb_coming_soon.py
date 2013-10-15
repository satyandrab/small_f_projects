#import urllib2
import mechanize
import cookielib
from lxml import html
import re
global count
count = 0

import csv
# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

data_writer = csv.writer(open("imdb coming soon.csv", "wb"))
data_writer.writerow(['URL', 'Title',
                      'URL of video',
                      'Rating',
                      'Rating from how many users',
                      'Certificate Rating (U/A, U, A)',
                      'Genre',
                      'Star cast',
                      'Director',
                      'Writer',
                      'Plot keywords',
                      'country',
                      'language',
                      'release date',
                      'Color (Black & White or color)',
                      'Animation (Animation movie or Simple)',
                      '3D (Is available in 3D or not)'])

def getMovieURL(url):
    print url
    html_response = br.open(url)
    html_source = html_response.read()
    result = html_source.replace('\n', '').replace('\r', '')
    f = open('test.html','w')
    f.write(result)
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    url_list = re.findall(r'<aonclick=.*?href="(/title/.*?/)".*?>', result)
    url_list = list(set(url_list))
#    print len(url_list)
    for landing_url in url_list:
        if '?' in landing_url:
            pass
        else:
#            print landing_url
            imdb('http://www.imdb.com'+str(landing_url))

def imdb(url):
    print url
    
    
    html_response = br.open(url)
    html_source = html_response.read()
    result = html_source.replace('\n', '').replace('\r', '')
    f = open('test.txt','w')
    f.write(result)
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    data_list = []
    
    """ URL """
    data_list.append(url)
    
    """ item_name """
    try:
        item_name = parsed_source.xpath("//td[@id='overview-top']/h1/text()")
        print item_name
        data_list.append("".join(item_name).strip())
    except:
#        raise
        data_list.append("")
        

    """ trailers and videos  """
    try:
        videogallery_url = url+'videogallery'
        videogallery_html_response = br.open(videogallery_url)
        videogallery_html_source = videogallery_html_response.read()
        videogallery_result = videogallery_html_source.replace('\n', '').replace('\r', '')
        videogallery_parsed_source = html.fromstring(videogallery_result, videogallery_url)
        videogallery_parsed_source.make_links_absolute()
        
        videogallery = videogallery_parsed_source.xpath("//div[@class='slate']/a/@href")
        videogallery = ", ".join(videogallery).strip()
        print videogallery
        data_list.append(videogallery)
    except:
#        raise
        data_list.append("")
        
    """ Rating """
    try:
        rating = parsed_source.xpath("//div[@class='titlePageSprite star-box-giga-star']/text()")
        print rating
        data_list.append("".join(rating).strip())
    except:
#        raise
        data_list.append("")

    """ Rating users"""
    try:
        rating_users = parsed_source.xpath("//span[@itemprop='ratingCount']/text()")
        print rating_users
        data_list.append("".join(rating_users).strip())
    except:
#        raise
        data_list.append("")

    """Certificate Rating (U/A, U, A)"""
    data_list.append("")
    
    """ Genres """
    try:
        Genres = parsed_source.xpath("//h4[contains(text(),'Genres:')]/following-sibling::a/text()")
        print Genres
        data_list.append(", ".join(Genres).strip())
    except:
#        raise
        data_list.append("")

    """ Stars """
    try:
        stars = parsed_source.xpath("//td[@itemprop='actor']/a/span/text()")
        print stars
        data_list.append(", ".join(stars[:-1]).strip())
    except:
#        raise
        data_list.append("")

    """ Director """
    try:
        director = parsed_source.xpath("//div[@itemprop='director']/a/span/text()")
        print director
        data_list.append("".join(director).strip())
    except:
#        raise
        data_list.append("")

    """ Writers """
    try:
        writers = parsed_source.xpath("//div[@itemprop='creator']/a/span/text()")
        print writers
        data_list.append("".join(writers).strip())
    except:
#        raise
        data_list.append("")

    """ Plot Keywords """
    try:
        plot_keywords = parsed_source.xpath("//span[@itemprop = 'keywords']/text()")
        print plot_keywords
        data_list.append(" , ".join(plot_keywords).strip())
    except:
#        raise
        data_list.append("")

    """ Country """
    try:
        country = parsed_source.xpath("//h4[contains(text(),'Country:')]/following-sibling::a/text()")
        print country
        data_list.append(", ".join(country).strip())
    except:
#        raise
        data_list.append("")

    """ language """
    try:
        language = parsed_source.xpath("//h4[contains(text(),'Language:')]/following-sibling::a/text()")
        print language
        data_list.append(", ".join(language).strip())
    except:
#        raise
        data_list.append("")

    """ release dates """
    try:
        release_dates_re = re.findall(r'<h4 class="inline">Release Date:</h4> (.*?)<', result)
        print release_dates_re
#        release_dates = release_dates_re.findall(str(release_dates_result))
        data_list.append(" ".join(release_dates_re).strip())
    except:
#        raise
        data_list.append("")

    """  Color """
    try:
        color = parsed_source.xpath("//div[h4[contains(text(),'Color:')]]/a/text()")
        print color
        data_list.append(", ".join(color).strip())
    except:
#        raise
        data_list.append("")
        
    """ Animation """
    try:
        animation = parsed_source.xpath("//h4[contains(text(),'Genres:')]/following-sibling::a/text()")
        print animation
        if ' Animation' in animation:
            data_list.append('animation')
        else:
            data_list.append('simple')
    except:
#        raise
        data_list.append("")

        data_list.append("")
        
    print '+'*78
    #try:
    temp_list = []
    for data_point in data_list:
        data = data_point.encode('utf-8')
        temp_list.append(data)
    
    if item_name:
        data_writer.writerow(temp_list)
        print temp_list
    #except:
    #    pass
    print '+'*78

if __name__ == '__main__':
    url = 'http://www.imdb.com/movies-coming-soon/'
    getMovieURL(url)

#    url = 'http://www.imdb.com/search/title?sort=moviemeter,asc&start=101&title_type=feature&year=2000,2000'
#    getMovieURL(url)
    
#    for i in range(1, 3600, 50):
#        print i
#        url = 'http://www.imdb.com/search/title?sort=moviemeter,asc&start='+str(i)+'&title_type=feature&year=2000,2000'
#        getMovieURL(url)