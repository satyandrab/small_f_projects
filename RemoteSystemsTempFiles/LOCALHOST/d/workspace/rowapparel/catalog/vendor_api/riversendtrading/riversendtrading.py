# -*- coding: utf-8 -*-
import urllib
import urllib2
import re

from pprint import pprint
from xml.etree import ElementTree

#import mechanize
from BeautifulSoup import BeautifulSoup#, Tag, NavigableString, Comment
#
try:
    from catalog.vendor_api import scraper_utils as utils
except:
    import utils

SLEEP_MIN = 1
SLEEP_MAX = 3

TESTRUN = True

BRAND_ALIASES = {
    'ashworth': ['aw'],
    'brooks brothers': ['brb'],
    'dri-duck': ['dri duck'],
    'forsyth': ['for'],
    'fruit of the loom': ['fruit'],
    'gildan': ['gil'],
    'jockey': ['jky'],
    'page & tuttle': ['pt'],
    "river's end": ['re'],
    "river's end activewear": ['re'],
    "river's end sport": ['re'],
    'storm creek': ['storm ck'],
    'tommy hilfiger': ['th'],
}


def _get_item_attributes(url_to_scrape, category_list = None, brand = None):
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(url_to_scrape)
    text = br.response().read()

    if TESTRUN: 
        print "Get Item Attributes"
        print url_to_scrape
    soup = BeautifulSoup(text, fromEncoding='iso-8859-1')
    text_without_newline = text.replace('\n','').replace('\r','').replace('\t','')
    
    product_id = soup.find('h1', {'class': 'prodtitlestylecode'})
    if product_id:
        product_id = product_id.text.lower()
    
    # Find title, if there's no title, assume that the page is blank and returns None
    if not soup.find('h1'):
        return None
    
    #Brand
    if brand:
        brand = brand
    else:
        brand_img = soup.find('div', {'class': 'prodMillImg'}).img
        brand = _get_all_brands(brand_img['src'])
        brand = brand.lower()
    
    # Find title
    try:
        title = re.findall(r'<h1 class="prodTitle.*?">(.*?)<',text_without_newline)#soup.find('h1', {'class': 'prodTitle'}).text#re.findall(r'<h1 class="prodTitle.*?">(.*?)<',text_without_newline)
        title = u"".join(title).lower().strip()
    except:
        title = soup.find('h1', {'class': re.compile(r'^prodTitle')}).text
        title = title.lower().strip()
    
    # Remove brand from title
    if re.findall(r'^'+brand+r'\b', title):
        title = title.replace(brand, '').strip()
    else:
        alias_list = BRAND_ALIASES.get(brand, [])
        for alias in alias_list:
            if re.findall(r'^'+alias+r'\b', title):
                title = title.replace(alias, '').strip()
    
    #find Category
    if category_list:
        category = category_list
    else:
        cate_list = []
        categories = soup.findAll('a', {'class': 'navlink'})
        for cate in categories:
            cate_list.append(cate.text.lower())
        category = cate_list[1:-1]

#    #find description_list
    description_list_temp = []
    description = None
    desc_div = soup.find('div', {'class': re.compile(r'^prodCatalogDesc')})
    first_li = desc_div.find('li')
    if first_li:
        desc_ul = first_li.parent
        for desc_li in desc_ul.findAll('li'):
            br_tag = desc_li.find('br')
            if br_tag:
                prev_sibling = br_tag.previousSibling
                if isinstance(prev_sibling, basestring):
                    description_list_temp.append(prev_sibling.strip())
            else:
                description_list_temp.append(desc_li.text)
    else:
        description = desc_div.text
    
    
#    #Size
    size_list = []
    size_list_t = re.findall(r'Available Sizes:</span> </span>(.*?)<', text_without_newline)
    size_list_t = "".join(size_list_t).split(',')
    for s in size_list_t:
        size_list.append(s.strip().lower())
    
    related_links = re.findall(r'<img class="compDetailImg".*?alt="(.*?)"',text_without_newline)
    tmp_related_links_list = []
    for item in related_links:
        related_dict = {}
        related_dict['relation'] = 'similar'
        related_dict['id'] = item.lower()
        tmp_related_links_list.append(related_dict)
    
    formatted_image_list = _process_images_data(url_to_scrape)
   
#    
    temp_attribute_dict = {}
    temp_attribute_dict['source_url'] = url_to_scrape 
    temp_attribute_dict['title'] = utils.unescape(title)
    if category:
        temp_attribute_dict['category'] = category
    if description:
        temp_attribute_dict['description'] = utils.unescape(description)
    temp_attribute_dict['description_list'] = [utils.unescape(desc_list) for desc_list in description_list_temp]
    temp_attribute_dict['available_sizes'] = size_list
    
    final_output = {}
    final_output['id'] = product_id
    final_output['brand'] = brand
    
    final_output['item_attributes'] = temp_attribute_dict
    final_output['item_images'] = formatted_image_list
    final_output['related_products'] = tmp_related_links_list

    return final_output

def _process_images_data(url):
    formatted_image_data = []
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(url)
    text = br.response().read()
    
    text_without_newline = text.replace('\n','').replace('\r','').replace('\t','')
    main_img = re.findall(r'<img id="mainProdImg.*?src="(.*?)"',text_without_newline)
    main_img = 'http://www.riversendtrading.com'+str("".join(main_img))
    
    # Build style url
    style_param = {}
    ptrn = r'(?<=&)(.+?)(?=&|$)'
    result = re.findall(ptrn, url)
    for param in result:
        #~ print param
        try:
            key, value = param.split('=')
            if key == 'product':
                style_param['style'] = value
            elif key in ['frames', 'target', 'sponsor']:
                style_param[key] = value
        except:
            pass
    
    style_url = 'http://www.riversendtrading.com/cgi-bin/liveweb/olc/get-style.w?'
    for key in ['style', 'frames', 'target', 'sponsor']:
        param = '%s=%s&'%(key, style_param[key])
        style_url += param
    
    br.open(style_url)
    text = br.response().read()

    main_image_found = False
    etree = ElementTree.XML(text)
    for elem in etree.iter('ttColor'):
        tmp_img = {}
        temp_img_dict = {}
        color_code = elem.attrib['colorCode'].lower()
        img_url = elem.attrib['imageLg']
        hex_color = elem.attrib['hexColor']
        hex_color_list = None
        if ',' in hex_color:
            hex_color_list = ['#'+clr for clr in hex_color.split(',')]
            hex_color = None
        elif hex_color:
            hex_color = '#'+str(hex_color)
        color_name = elem.attrib['description'].lower()
        if color_name.endswith(' - discontinued'):
            color_name = color_name.replace(' - discontinued', '')
        
        if img_url:
            image_url = 'http://www.riversendtrading.com'+str(img_url)
            if image_url == main_img:
                main_image_found = True
                temp_img_dict['attributes'] = {'main': True}
                temp_img_dict['image_url'] = image_url
            else:
                temp_img_dict['attributes'] = {'main': False}
                temp_img_dict['image_url'] = image_url
        
        tmp_img['images'] = []
        if temp_img_dict:
            tmp_img['images'].append(temp_img_dict)
        
        color_dict = {}
        color_dict['color'] = { 'name': color_name, 'color_id': color_code}
        if hex_color:
            color_dict['color']['hex'] = hex_color
        elif hex_color_list:
            color_dict['color']['hex_list'] = hex_color_list
        tmp_img['attributes'] = color_dict
        formatted_image_data.append(tmp_img)
    
    if not main_image_found:
        # If main image is not included, add main image to list
        if main_img:
            formatted_image_data.insert(0, {
                'attributes': {'color': {'name': ''}}, 
                'images': [{'attributes': {'main': True}, 'image_url': main_img}]})
    
    return formatted_image_data

#    
def _traverse_categories():
#    all_product_url_list = []
    traverse_categories_output_dict = {}
    """
        Find item ids, categories and urls by traversing category pages.
        Returns { item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
    """
    
    category_url = "http://www.riversendtrading.com/cgi-bin/liveweb/site.w?sponsor=000001&top=catalog&target=main&frames=no"
    cat_page_html_as_text = urllib2.urlopen(category_url).read().replace('\n','').replace('\r','').replace('\t','')
    
    cat_urls = re.findall(r'menuSide"><a class="catTitle" href="(.*?)"\s+title.*?>(.*?)</a>',cat_page_html_as_text)
    
#    list_cat_url = []
    for item in cat_urls:
        cat_urls =  'http://www.riversendtrading.com' + item[0]
        category_1 = item[1].lower().strip()
        cat_urls_text = urllib2.urlopen(cat_urls).read().replace('\n','').replace('\r','').replace('\t','')
        inner_cat_urls = re.findall(r'featDetailTitle" href="(.*?)"\s+title.*?>(.*?)</a>' , cat_urls_text)
        for inner_url in inner_cat_urls:
            all_cat_urls =  'http://www.riversendtrading.com' + inner_url[0]+'#all'
            category_2 = inner_url[1].lower().strip().replace("'",'')
            category_list = [category_1, category_2]

            main_category_url = str(all_cat_urls)
            br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
            main_cat_page_html_as_text = br.open(main_category_url).read().replace('\n','').replace('\r','').replace('\t','')
          
            products_details = re.findall(r'productLink.*?href="(.*?)">.*?id="(.*?)"',main_cat_page_html_as_text)
            
            for item in products_details:
                temp_dict = {}
                url = 'http://www.riversendtrading.com' + item[0].replace(",'main')","").replace("javascript:golink('",'').strip()
                url = url.split('althref="')[0].strip()
                pid = item[1].replace('img','').replace('Price','').strip().lower()
                temp_dict['id'] = pid
                temp_dict['url'] = url.replace('"','')
                temp_dict['category_list'] = category_list
                if TESTRUN:print temp_dict
                traverse_categories_output_dict[pid] = temp_dict
    
    brand_output_categories = _traverse_categories_brand()
    for brand_url in brand_output_categories:
        if brand_url['id'] in traverse_categories_output_dict.keys():
            traverse_categories_output_dict[brand_url['id']]['brand'] = brand_url['brand']
            if TESTRUN:
                print '^'*78
                print traverse_categories_output_dict[brand_url['id']]
                print '^'*78
        else:
            traverse_categories_output_dict[brand_url['id']] = brand_url

#    if TESTRUN:
#        open_test = open('test.txt', 'wb')
#        open_test.write(str(traverse_categories_output_dict))
    return traverse_categories_output_dict

def _traverse_categories_brand():
    final_brand_prod_url = []
    category_names = None
    """
Find item ids, categories and urls by traversing category pages.
Returns { item_id: { 'id': item_id, 'brand': brand, 'url': item_url } }
"""
    brand_seed_page = 'http://www.riversendtrading.com/cgi-bin/liveweb/site.w?location=olc/brands.w&frames=no&target=main&sponsor=000001'
    
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open(brand_seed_page)
    html_response = browser.response().read()
    
    soup = BeautifulSoup(html_response)
    
    anchor = soup.findAll('a', {'class': 'brandLink'})
    for brand_names in anchor:
        brand_name = brand_names.img['alt']
        temp_brand_url = brand_names['href']
        mill = ''
        if '&mill=' in temp_brand_url:
            mill = temp_brand_url.split('&mill=')[1].split('&')[0]
            brand_url = "http://www.riversendtrading.com/cgi-bin/liveweb/olc/search-browse.w?hidetime=yes&frames=no&mill="+mill+"&target=main&sponsor=000001"
            pagination_urls = _get_pagination_url(brand_url, mill)
            if TESTRUN:
                print '*'*80
                print pagination_urls
                print '*'*80
            for pagination_url in pagination_urls:
                returned_brand_prod_url = _get_products_url(pagination_url, mill, category_names, brand_name = brand_name)
                if TESTRUN:print returned_brand_prod_url
                final_brand_prod_url.extend(returned_brand_prod_url)

    return final_brand_prod_url

def _get_products_url(category_url, mill, category_name=None, brand_name=None):
    product_list = []
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
#    if TESTRUN:
#        print category_url
    brand_url = "http://www.riversendtrading.com/cgi-bin/liveweb/site.w?location=olc/guided-search.w&mill="+str(mill)+"&frames=no&target=main&sponsor=000001"
    br.open(brand_url)
    br.open(category_url)
    text = br.response().read()

    soup = BeautifulSoup(text)
    
    if category_name:
        category = category_name
    
    products_details = soup.findAll('a', {'class': 'productLink'})
    for product_detail in products_details:
        temp_product_dict = {}
        temp_product_dict['url'] = 'http://www.riversendtrading.com'+product_detail['href']
        try:
            temp_product_dict['id'] = product_detail['href'].split('&product=',1)[1].split('&')[0].strip().lower()
        except:
            temp_product_dict['id'] = ''
            raise
        if category_name:
            temp_product_dict['category_list'] = [str(category)]
        if brand_name:
            temp_product_dict['brand']= brand_name.lower()
        product_list.append(temp_product_dict)
    return product_list

def _get_pagination_url(brand_url, mill):
    pagination_url = []
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open("http://www.riversendtrading.com/cgi-bin/liveweb/site.w?location=olc/guided-search.w&mill="+mill+"&frames=no&target=main&sponsor=000001")
    browser.open(brand_url)
    html_response = browser.response().read()
    soup = BeautifulSoup(html_response)
    try:
        anc_page = soup.findAll('a',{'class':'pageNumbers'})
        max_page_num = int(anc_page[-2].text)
    except:
        max_page_num = 1
    
    for i in range(1,max_page_num+1):
        page_url = brand_url+"&page="+str(i)
        pagination_url.append(page_url)
    
    return pagination_url
    
    
def get_urls(cached_data=None):
    """
        Get all item ids and urls.
        Returns [ {'id': string, 'url': string}, ]
    """
    if cached_data:
        cat_dict = cached_data['categories_dict']
    else:
        # Get data from traversing category pages
        cat_dict = _traverse_categories()   # {id: { 'id': id, 'category_list': [categories], 'url': url } }
    
    return cat_dict.values()


def get_cached_data():
    data = {
#            'csv_dict': _get_csv_data()
        'categories_dict': _traverse_categories(),
#        'color_data': _get_color_data(),
            }
    return data

def _get_all_brands(brand_logo):
    brand_dict = {}
    brand_page = 'http://www.riversendtrading.com/cgi-bin/liveweb/site.w?location=olc/brands.w&frames=no&target=main&sponsor=000001'
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(brand_page)
    text = br.response().read()

    if TESTRUN: print "Get all brands"
    soup = BeautifulSoup(text)
    
    brand_list = soup.findAll('img', {'class':'brandImage'})
    for brand in brand_list:
        brand_dict[brand['src']] = brand['alt']
    
    if brand_dict.has_key(brand_logo):
        return brand_dict[brand_logo]
    
def scrape(url_to_scrape = None, cached_data = None):
    """
        Scrape riversendtrading.com. If url is set, scrape only item in the url
        If url_to_scrape is not set, returns list of itemInfo dict
        If url_to_scrape is set, returns itemInfo dict
    """
    all_items = []
    
    if cached_data:
        cat_dict = cached_data['categories_dict']
    else:
        cat_dict = _traverse_categories()   # {item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
        
#    category_list = []
    if url_to_scrape:
        for scrape_cat_data in cat_dict.values():
            if scrape_cat_data['url'] == url_to_scrape:
                if scrape_cat_data.has_key('category_list'):
                    category_list = scrape_cat_data['category_list']
                if scrape_cat_data.has_key('brand'):
                    brand = scrape_cat_data['brand']
                break
        # Only include item to scrape
        if scrape_cat_data.has_key('category_list') and scrape_cat_data.has_key('brand'):
            scrape_data_output = _get_item_attributes(url_to_scrape, category_list, brand)
        elif scrape_cat_data.has_key('category_list'):
            scrape_data_output = _get_item_attributes(url_to_scrape, category_list)
        else:
            scrape_data_output = _get_item_attributes(url_to_scrape)
        return scrape_data_output
    
    else:
        for scrape_cat_data in cat_dict.values():
            if scrape_cat_data.has_key('category_list'):
                category_list = scrape_cat_data['category_list']
            if scrape_cat_data.has_key('brand'):
                brand = scrape_cat_data['brand']
                
            if category_list and brand:
                scrape_data_output = _get_item_attributes(scrape_cat_data['url'], category_list, brand)
            elif category_list:
                scrape_data_output = _get_item_attributes(scrape_cat_data['url'], category_list)
            else:
                scrape_data_output = _get_item_attributes(scrape_cat_data['url'])
                
            if TESTRUN:
                print "URL is not set so scrapping data from :- ", scrape_cat_data['url']
                print '-'*78
                print get_all_data_points
                print '-'*78
            all_items.append(get_all_data_points)
        return all_items
