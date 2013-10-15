# -*- coding: utf-8 -*-

#import mechanize
from BeautifulSoup import BeautifulSoup#, Tag, NavigableString, Comment
import re
from xml.dom.minidom import parseString#
try:
    from catalog.vendor_api import scraper_utils as utils
except:
    import utils

SLEEP_MIN = 1
SLEEP_MAX = 3

TESTRUN = True

def _get_item_attributes(url_to_scrape, category_list = None, brand = None):
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(url_to_scrape)
    text = br.response().read()

    if TESTRUN: print "Get Item Attributes"
    soup = BeautifulSoup(text)
    text_without_newline = text.replace('\n','').replace('\r','').replace('\t','')
    
    product_id = soup.find('b', {'class': 'orangeStyle'}).text.lower()

    # Find title
    temp_title = soup.findAll('b', {'class':'darkBold'})
    size_range = temp_title[0].text.lower().replace(':','')
    title = temp_title[1].text.lower().split(u'\xae')
    title = " ".join(title)

    #find Category
    category = []
    if category_list:
        category = category_list
    else:
        temp_category = soup.findAll('a', {'class':'breadCrumbs'})
        for cat in temp_category:
            category.append(cat.text.lower())
            
    if brand:
        brand = brand

    
    #find Description
    desc = re.findall(r'<b class="smallBlueText">Description:</b>(.*?)</td>', text_without_newline)
    description = "".join(desc).replace('&nbsp;', '').strip()
    
    temp_desc_list = []
    desc_list = soup.findAll('b', {'class':'tddata'})
    for d_list in desc_list:
        temp_desc_list.append(d_list.text)
    
    #size list
    sizes = []
    temp_size_list = soup.find('td', {'id':'sizeImages'})
    for size in temp_size_list.findAll('img'):
        sizes.append("".join(re.findall(r'/details/(.*?).gif', size['src'])))
    
    formatted_img_data = _get_image_data(soup)
    
    related_products = _get_related_products(soup)
    
    
    temp_attribute_dict = {}
    temp_attribute_dict['source_url'] = url_to_scrape 
    temp_attribute_dict['title'] = title
    if category:
        temp_attribute_dict['category'] = category
    temp_attribute_dict['description'] = description 
    temp_attribute_dict['description_list'] = temp_desc_list
    temp_attribute_dict['available_sizes'] = sizes
    temp_attribute_dict['size_range'] = size_range
    
    final_output = {}
    final_output['id'] = product_id
    if brand:
        final_output['brand'] = brand
    
    final_output['item_attributes'] = temp_attribute_dict
    final_output['item_images'] = formatted_img_data
    final_output['related_products'] = related_products
    
    return final_output
    
def _get_image_data(img_soup):
    formatted_img_list = []
    main_img = img_soup.find('img', {'id': 'sim2'})['src']
    main_image_data = { 'images': [
                                   {'attributes': {'main': True}, 'image_url': main_img},
                                   ],
                       'attributes': { 'color': { 'name': '', 'hex': '', 'color_id': ''} }
                       }
    formatted_img_list.append(main_image_data)
    get_swatch_info = img_soup.findAll('td', {'class': 'swatchCell'})
    for sw in get_swatch_info:
        hex = sw['bgcolor']
        color_code = re.findall(r"loadImage\('(.*?)', '(.*?)', '(.*?)'\)", sw.a['href'])[0][0]
        prod_id = re.findall(r"loadImage\('(.*?)', '(.*?)', '(.*?)'\)", sw.a['href'])[0][1].strip()
        color_name = re.findall(r"loadImage\('(.*?)', '(.*?)', '(.*?)'\)", sw.a['href'])[0][2].lower()
        img_url = 'http://www.bodekandrhodes.com/96live/assets/images/still/zoom/'+prod_id+'_'+color_code+'_zm.jpg'
        sub_image_data = { 'images': [
                                   {'attributes': {'main': False}, 'image_url': img_url},
                                   ],
                       'attributes': { 'color': { 'name': color_name, 'hex': hex, 'color_id': color_code} }
                       }
        formatted_img_list.append(sub_image_data)
    return formatted_img_list

def _get_related_products(rel_prod_soup):
    related_prod_final = []
    related_prod = rel_prod_soup.findAll('span', {'class': 'coordStyleNum'})
    for rel_prod in related_prod:
        temp_dict = {}
        temp_dict['id'] = rel_prod.text.lower()
        temp_dict['relation'] = 'similar'
        related_prod_final.append(temp_dict)
    return related_prod_final

def _traverse_categories():
#    """
    final_traversed_dict = {}
    """
        Find item ids, categories and urls by traversing category pages.
        Returns { item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
    """
    site_map_url = 'http://www.bodekandrhodes.com/96live/statichtml/ns_sitemap.html'
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(site_map_url)
    main_cat_page_html_as_text = br.response().read().replace('\n','').replace('\r','')
    
    main_cat_url = re.findall(r"""golink\('(olc/catalog-browse.w\?category=.*?)','main'\)">(.*?)</a>""", main_cat_page_html_as_text)
    for main_cat in main_cat_url:
        cat_name = main_cat[1].lower()
        main_cat = main_cat[0].replace('browse.w?category=', 'browse.w&category=')
        cat_url = 'http://www.bodekandrhodes.com/cgi-bin/barlive/site.w?location='+main_cat+'&frames=no&target=main&sponsor=000001&nocache=45327'
        if TESTRUN:
            print cat_url
            print cat_name
            print '-'*78
        br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
        br.open(cat_url)
        text = br.response().read()
        soup = BeautifulSoup(text)
        temp_find_subcat = soup.findAll('td', {'class': 'catSpace'})
        for sub_cat in temp_find_subcat:
            try:
                #print sub_cat
                sub_cat_url_name = re.findall(r"""golink\('(/cgi-bin/barlive/olc/catalog-browse.w\?category=.*?)'.*?>(.*?)</a>""", str(sub_cat))
                url_sub_cat = sub_cat_url_name[0][0].replace('&amp;', '&').replace('browse.w?category=', 'browse.w&category=')
                sub_cat_url = 'http://www.bodekandrhodes.com/cgi-bin/barlive/site.w?location='+url_sub_cat+'&frames=no&target=main&sponsor=000001&nocache=45327&page=all'
                sub_cat_name = sub_cat_url_name[0][1].lower()
                #print sub_cat_url
                #print sub_cat_name
                sub_br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
                sub_br.open(sub_cat_url)
                text = sub_br.response().read()
                sub_soup = BeautifulSoup(text)
                
                prod_data = sub_soup.findAll('a', {'class': 'orangeStyle'})
                for prod in prod_data:
                    try:
                        temp_dict = {}
                        prod_id_url = re.findall(r"""golink\('(olc/cobrand-product.w\?category=.*?product=.*?)'.*?>(.*?)</a>""", str(prod))
                        prod_url = prod_id_url[0][0].replace('&amp;', '&').replace('product.w?category=', 'product.w&category=')
                        products_url = 'http://www.bodekandrhodes.com/cgi-bin/barlive/site.w?location='+prod_url+'&frames=no&target=main&sponsor=000001&nocache=45327'
                        prod_id = prod_id_url[0][1].lower()
                        temp_dict['id'] = prod_id
                        temp_dict['url'] = products_url
                        temp_dict['category_list'] = [cat_name, sub_cat_name]
                        if TESTRUN:
                            print temp_dict
                            print '*'*78
                        final_traversed_dict[prod_id] = temp_dict
                    except:
                        pass
            except:
#                raise
                pass
    
    brand_output_categories = _traverse_categories_brand()
    for k, v in brand_output_categories.items():
        print k, v
        print '*'*78
        if final_traversed_dict.has_key(k):
#        if brand_url['id'] in final_traversed_dict.keys():
            final_traversed_dict[k]['brand'] = v['brand']
            if TESTRUN:
                print '^'*78
                print final_traversed_dict[k]
                print '^'*78
        else:
            final_traversed_dict[k] = v
    return final_traversed_dict
    
def _traverse_categories_brand():
    try:
        final_traversed_dict_brand = {}
        """
            Find item ids, categories and urls by traversing category pages.
            Returns { item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
        """
        
        brand_url = 'http://www.bodekandrhodes.com/96live/xml/brands.xml'
        br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
        br.open(brand_url)
        main_cat_page_html_as_text = br.response().read()
        
        dom = parseString(main_cat_page_html_as_text)
        xmlTag = dom.getElementsByTagName('brand')
        for xml_tag in xmlTag:
            brand_name = re.sub(r'<.*?>', '', xml_tag.getElementsByTagName('name')[0].toxml()).lower()
            cat_id = re.findall(r'<category type="cat"><!\[CDATA\[ (.*?) \]\]></category>',xml_tag.getElementsByTagName('category')[0].toxml())
            brand_brand_url = 'http://www.bodekandrhodes.com/cgi-bin/barlive/site.w?location=olc/catalog-browse.w&category='+"".join(cat_id)+'&frames=no&target=main&sponsor=000001&nocache=45327&page=all'
            br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
            br.open(brand_brand_url)
            text = br.response().read()
            soup = BeautifulSoup(text)
            prod_data = soup.findAll('a', {'class': 'orangeStyle'})
            for prod in prod_data:
                temp_dict = {}
                prod_id_url = re.findall(r"""golink\('(olc/cobrand-product.w\?category=.*?product=.*?)'.*?>(.*?)</a>""", str(prod))
                prod_url = prod_id_url[0][0].replace('&amp;', '&').replace('product.w?category=', 'product.w&category=')
                products_url = 'http://www.bodekandrhodes.com/cgi-bin/barlive/site.w?location='+prod_url+'&frames=no&target=main&sponsor=000001&nocache=45327'
                prod_id = prod_id_url[0][1].lower()
                temp_dict['id'] = prod_id
                temp_dict['url'] = products_url
                temp_dict['brand'] = brand_name
                final_traversed_dict_brand[prod_id] = temp_dict
        return final_traversed_dict_brand
    except:
        pass

def scrape(url_to_scrape=None, cached_data=None):
    """
        Scrape independenttradingco.com. If url is set, scrape only item in the url
        If url_to_scrape is not set, returns list of itemInfo dict
        If url_to_scrape is set, returns itemInfo dict
    """
    all_items = []
    
    if cached_data:
        cat_dict = cached_data['categories_dict']
    else:
        cat_dict = _traverse_categories()   # {item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
    category_list = brand = None
    if url_to_scrape:
        for scrape_cat_data in cat_dict.values():
            if scrape_cat_data['url'] == url_to_scrape.encode('utf-8'):
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
            if scrape_cat_data.has_key('category_list') and scrape_cat_data.has_key('brand'):
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'], scrape_cat_data['category_list'], scrape_cat_data['brand'])
            elif scrape_cat_data.has_key('category_list'):
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'], scrape_cat_data['category_list'])
            else:
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'])
            if TESTRUN:
                print "URL is not set so scrapping data from :- ", scrape_cat_data['url']
                print '-'*78
                print get_all_data_points
                print '-'*78
            all_items.append(get_all_data_points)
        return all_items
        
def get_cached_data():
    data = {
            'categories_dict': _traverse_categories(),
            }
    return data

def get_urls(cached_data=None):
    """
    Get all item ids and urls.
    Returns [ {'id': string, 'url': string}, ]
    """
    if cached_data:
        cat_dict = cached_data['categories_dict']
    else:
        # Get data from traversing category pages
        cat_dict = _traverse_categories() # {id: { 'id': id, 'category_list': [categories], 'url': url } }
    
    return cat_dict.values()

