# -*- coding: utf-8 -*-
import re
import time
import random
import tarfile
import csv
import shutil
import os
import datetime
#import mechanize
from BeautifulSoup import BeautifulSoup, UnicodeDammit
#
try:
    from catalog.vendor_api import scraper_utils as utils
except:
    import utils

SLEEP_MIN = 1
SLEEP_MAX = 3

TESTRUN = True

USERNAME = 'rowapparel'
PASSWORD = 'rowapparel650'

def _traverse_categories():
    """
        Find item ids, categories and urls by traversing category pages.
        Returns { item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url, 'brand':brand } }
    """
    
    csv_output_dict = _get_csv_data()
    print csv_output_dict.keys()
    #~ if csv_output_dict:
        #~ return csv_output_dict
    #~ else:
    final_output_url_list = []
    traverse_cat_output = {}
    #    brand_seed_page = 'https://www.broderbros.com/cgi-bin/online/webshr/browse-brand-all.w'
    seed_page = 'https://www.broderbros.com/cgi-bin/online/webshr/browse-category-all.w'
    
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open(seed_page)
    html_response = browser.response().read()
    
    soup = BeautifulSoup(html_response)
    
    all_category_names = soup.findAll('div', {'class': 'brwsBrndLogoClip'})
    for category_names in all_category_names:
        temp_category_url = str(category_names.a['href'])
        category_url_name = temp_category_url.split('&catname=')[-1]
        category_url = 'https://www.broderbros.com/cgi-bin/online/webshr/search-result.w?nResults=5000&mc=&RequestAction=advisor&RequestData=CA_CategoryExpand&bpath=c&CatPath=All Products////BRO-Categories////'+str(category_url_name)
        category_url = category_url.replace(' ', '%20')
        category_names = category_names.a.img['alt'].lower()
        returned_url_list = _get_product_urls(category_url, category_names)
        final_output_url_list.extend(returned_url_list)
        
    for productsurl in final_output_url_list:
        if productsurl['id'] in traverse_cat_output.keys() and productsurl['category_list'] != traverse_cat_output[productsurl['id']]['category_list']:
            traverse_cat_output[productsurl['id']]['category_list'].extend(productsurl['category_list'])
        else:
            traverse_cat_output[productsurl['id']] = productsurl
    
    brand_output_categories = _traverse_categories_brand()
    for brand_url in brand_output_categories:
        if brand_url['id'] in traverse_cat_output.keys():
            traverse_cat_output[brand_url['id']]['brand'] = brand_url['brand']
        else:
            traverse_cat_output['id'] = brand_url
    
    if TESTRUN:
        for k,v in traverse_cat_output.items():
            print v
            print '*'*78
    for item_id in traverse_cat_output.keys():
        print item_id
        csv_data = csv_output_dict.get(item_id)
        if csv_data:
            traverse_cat_output[item_id]['brand'] = csv_data['brand']
        if not traverse_cat_output[item_id].get('brand'):
            del traverse_cat_output[item_id]
    
    return traverse_cat_output

def _get_product_urls(category_url, category_name=None, brand_name = None):
    
    temp_product_list = []
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open(category_url)
    html_response = browser.response().read()
    soup = BeautifulSoup(html_response)

    find_all_product_url = soup.findAll('a', {'class': 'one'})
#    print find_all_product_url
    for products_url in find_all_product_url:
        product_label_dict = {}
        product_id = products_url.span.text
        if TESTRUN:
            print "extracted product data.............."+ str(product_id)
            print '*'*78
        product_url = 'https://www.broderbros.com/cgi-bin/online/webshr/prod-detail.w?sr='+str(product_id)
        product_label_dict['id'] = product_id.strip().lower()
        product_label_dict['url'] = product_url
        if category_name:
            product_label_dict['category_list'] = [category_name.lower()]
        if brand_name:
            product_label_dict['brand'] = brand_name.lower()
        temp_product_list.append(product_label_dict)
        
    return temp_product_list

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
        cat_dict = _traverse_categories()   # {id: { 'id': id, 'category_list': [categories], 'url': url } }
    
#    if TESTRUN:
#        for v in cat_dict.values():
#            print v
#            print "-"*78
            
    return cat_dict.values()

def _traverse_categories_brand():
    final_output_url_brand_list = []
    category_names = None
    """
        Find item ids, categories and urls by traversing category pages.
        Returns { item_id: { 'id': item_id, 'brand': brand, 'url': item_url } }
    """

    brand_seed_page = 'https://www.broderbros.com/cgi-bin/online/webshr/browse-brand-all.w'
    
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open(brand_seed_page)
    html_response = browser.response().read()
    
    soup = BeautifulSoup(html_response)
    
    all_brand_names = soup.findAll('div', {'class': 'brwsBrndLogoClip'})
    for brand_names in all_brand_names:
#        temp_brand_url = str(brand_names.a['href'])
        brand_name = brand_names.a.img['alt'].lower()
        brand_name_url = brand_name.replace('&', "%26")
        brand_url = "https://www.broderbros.com/cgi-bin/online/webshr/search-result.w?nResults=1000&mc=LB&RequestAction=advisor&RequestData=CA_BreadcrumbSelect&currentpage=1&bpath=b&CatPath=All Products////AttribSelect%3DMill %3D'"+str(brand_name_url)+"'////BRO-Categories"
        brand_url = brand_url.replace(' ', '%20')
        returned_url_brand_list = _get_product_urls(brand_url, category_names, brand_name = brand_name)
        final_output_url_brand_list.extend(returned_url_brand_list)
        
    return final_output_url_brand_list

def _get_item_attributes(url_to_scrape, category_list = None, brand_listed = None):
    print url_to_scrape
    
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    br.open(url_to_scrape)
    text = br.response().read()

    if TESTRUN: print "Get Item Attributes"
    soup = BeautifulSoup(text)
    text_without_newline = text.replace('\n','').replace('\r','').replace('\t','')
    
    #id
    product_id_raw = soup.find('h1').text
    product_id = product_id_raw.lower()
    
    #brand
    temp_brand = ''
    if brand_listed:
        brand = brand_listed
        temp_brand = brand
    else:
        brand = re.findall(r'BRO-Categories">.*?alt="(.*?)"', text_without_newline)
        temp_brand = "".join(brand)
        brand = temp_brand.lower()

    # Find title
    title = re.findall(r'</h1>\s*<span>(.*?)</span>', text_without_newline)
    title = [UnicodeDammit(subtitle).unicode for subtitle in title]    # Change to utf-8
    title = u"".join(title).replace(product_id_raw, '').replace(temp_brand, '').strip()    # Remove item id and brand
    title = utils.unescape(title)
    #find Category
    if category_list:
        category = category_list 

    #find description list
    desc_list = []
    try:
        temp_desc_list = soup.find('div', {'id': 'overview'}).ul
        for li in temp_desc_list:
            if li != '\n':
                desc_txt = unicode(re.sub(r'<.*?>', '', str(li)), 'utf-8')
                desc_data = utils.unescape(desc_txt)
                desc_list.append(desc_data)
    except:
        desc_list = []
        
    
    #find description
    desc = None
    try:
        temp_desc = soup.find('div', {'id': 'overview'}).p.text
        if 'Virtual Sample' in temp_desc:
            desc = None
        else:
            desc = utils.unescape(temp_desc)
    except:
        desc = None

    #find sizes
    size_list = []
    sizes = soup.findAll('td', {'width': '33%'})
    for size in sizes:
        size_list.append(size.text.lower())
    available_sizes = list(set(size_list))
    
    #find related products
    related_product_list = []
    find_comparable_products_id = soup.findAll('span', {'class': 'txtBold'})
    for comparable_products_id in find_comparable_products_id:
        rel_pro_dict = {}
        rel_pro_dict['id'] = comparable_products_id.text.lower()
        rel_pro_dict['relation'] = 'similar'
        related_product_list.append(rel_pro_dict)
    
    find_companions_products = re.findall(r'<p><strong>Companions:</strong>.*?</a></p>', text_without_newline)
    for companion_products in "".join(find_companions_products).split('</a>'):
        get_product_id_and_relation = re.findall(r'">(.*?)\((.*?)\)', str(companion_products))
        if get_product_id_and_relation:
            for companion_products in get_product_id_and_relation:
                temp_companion_dict = {}
                temp_companion_dict['id'] = companion_products[0].lower()
                temp_companion_dict['relation'] = companion_products[1].lower()
                related_product_list.append(temp_companion_dict)
    
    #find color information
    color_seed_page = 'https://www.broderbros.com/cgi-bin/online/webshr/colorChart.w?sc='+str(product_id)
    
    browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    browser.open(color_seed_page)
    html_response = browser.response().read().replace('\n', '').replace('\r', '')
    
    color_dict = {}
    temp_color_tr = re.findall(r'<a href="https://www.broderbros.com/cgi-bin/online/webshr/colorChart.w\?sc=.*?&color=(.*?)">(.*?)</a>\s*</td>\s*<td bgcolor="(.*?)">', html_response)
    for color_tr in temp_color_tr:
        temp_color_dict = {}
        color_id = color_tr[0].lower()
        color_name = color_tr[1].replace('&nbsp', ' ').replace(';', '').strip().lower()
        color_hex = color_tr[2].lower()
        temp_color_dict['name'] = color_name
        temp_color_dict['hex'] = color_hex.lower()
        temp_color_dict['color_id'] = color_id
        color_dict[color_id] = temp_color_dict
        
    #Find Main Image
    main_image = soup.find('div', {'class': 'photoBg'}).img['src']
    main_image_url = 'https://www.broderbros.com'+str(main_image)

    #find image information
    #https://www.broderbros.com/cgi-bin/online/webshr/prod-gallery.w?sr=G200
    image_seed_page = 'https://www.broderbros.com/cgi-bin/online/webshr/prod-gallery.w?sr='+str(product_id)
    
    image_browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    image_browser.open(image_seed_page)
    gallery_html_response = image_browser.response().read()
    
#    image_soup = BeautifulSoup(gallery_html_response)
    
    images_list = re.findall(r'(/images/bro/prodGallery/.*?.jpg)', gallery_html_response)
    images_list = list(set(images_list))

    formatted_images = _format_images(images_list, color_dict, main_image_url)
    
    title = title.lower()
    brand = brand.lower()
    if title.startswith(brand):
        title = title.replace(brand, '', 1).strip()
    
    final_output = {}
    temp_data_dict = {}
    temp_data_dict['source_url'] = url_to_scrape 
    temp_data_dict['title'] = title
    if category_list:
        temp_data_dict['category'] = category_list
    if desc_list:
        temp_data_dict['description_list'] = desc_list
    if desc:
        if desc != 'Color Chart':
            temp_data_dict['description'] = desc
    if size_list:
        temp_data_dict['available_sizes'] = available_sizes
#    temp_data_dict['retail_price'] = retail_price

    final_output['id'] = product_id
    final_output['brand'] = brand
    final_output['item_attributes'] = temp_data_dict
    final_output['item_images'] = formatted_images
    final_output['related_products'] = related_product_list
    
    return final_output

    
def _format_images(images_list, color_dict, main_image_url):
    temp_main_image_dict = {}
    formatted_image_list = []
    temp_main_image_dict['images'] = [ {'attributes': {'main': True}, 'image_url': main_image_url}]
    #color information not given logically on page so need to enter manually for main image
    #tried without attributes key but its raising an error so put an blank in the color name, please update the code if required.  
    temp_main_image_dict['attributes'] = {'color' : {'name':''}}
    
    formatted_image_list.append(temp_main_image_dict)
    for image in images_list:
        image_url = 'https://www.broderbros.com'+str(image).replace('/prodGallery/', '/prodDetail/').replace('_g.', '_p.')
        color_id_from_img = image_url.split('_')[-2]
        if color_dict.has_key(color_id_from_img):
            main_img_dict = {}
            main_img_dict['images'] = [ {'attributes': {'main': True}, 'image_url': image_url}]
            color_dict[color_id_from_img].pop('color_id')
            main_img_dict['attributes'] = {'color' : color_dict[color_id_from_img]}
            formatted_image_list.append(main_img_dict)

#    for image in formatted_image_list:
#        print image
#        print '-'*78
    return formatted_image_list

def scrape(url_to_scrape=None, cached_data=None):
    
    """
        Scrape charlesriverapparel.com. If url is set, scrape only item in the url
        If url_to_scrape is not set, returns list of itemInfo dict
        If url_to_scrape is set, returns itemInfo dict
    """
    all_items = []
    
    if cached_data:
        cat_dict = cached_data['categories_dict']
    else:
        cat_dict = _traverse_categories()   # {item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url } }
    
    category_list = None
    brand = None
    if url_to_scrape:
        for scrape_cat_data in cat_dict.values():
            if scrape_cat_data['url'] == url_to_scrape:
                if scrape_cat_data.has_key('category_list'):
                    category_list = scrape_cat_data['category_list']
                else:
                    category_list = None
                    
                if scrape_cat_data.has_key('brand'):
                    brand = scrape_cat_data['brand']
                else:
                    brand = None
                break
        # Only include item to scrape
        if category_list and brand:
            scrape_data_output = _get_item_attributes(url_to_scrape, category_list, brand)
        elif category_list:
            scrape_data_output = _get_item_attributes(url_to_scrape, category_list)
        else:
            scrape_data_output = _get_item_attributes(url_to_scrape)
        return scrape_data_output
    
    else:
        for scrape_cat_data in cat_dict.values():
            if scrape_cat_data.has_key('category_list'):
                category_list = scrape_cat_data['category_list']
            else:
                category_list = None
            
            if scrape_cat_data.has_key('brand'):
                brand = scrape_cat_data['brand']
            else:
                brand = None
            
            if category_list and brand:
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'], category_list, brand)
            elif category_list:
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'], category_list)
            else:
                get_all_data_points = _get_item_attributes(scrape_cat_data['url'])
                
            if TESTRUN:
                print "URL is not set so scrapping data from :- ", scrape_cat_data['url']
                print '-'*78
                print get_all_data_points
                print '-'*78
            all_items.append(get_all_data_points)
    return all_items

def _get_csv_data():
    """ 
        Get item ids and urls from csv. If csv failed to download,.
        Returns { item_id: { 'id': item_id, 'category_list': [categories], 'url': item_url, 'brand':brand } } if csv download fails return None so that _traverse_category can be used. 
    """
    temp_dir = './catalog/vendor_caches'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    
    csv_output_dict = {}
    
    print 'Downloading csv file...'
    br = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
    
    if TESTRUN: print 'Load Login Page'
    br.open("https://www.broderbros.com/cgi-bin/online/webbro/bro-index.w")
#    br.response().read()
    try:
        # Fill login form
        br.select_form(name = 'frmLogin')
        frm = br.form
        
        ctrl = frm.find_control('userName')
        ctrl.value = USERNAME
        ctrl = frm.find_control('password')
        ctrl.value = PASSWORD
    
        # Submit login form
        if TESTRUN: print 'Submit Login Form'
    
        br.select_form(name = 'frmLogin')
        br.submit()
    except:
        print "Login form does not exist, please check URL, downloaded html or site is down"
        return None
    
    # Simulate js for setting cookies
    utmn = str(int(random.random()*4294967295))
    utmu = str(int(time.time()/1000))
    utm1 = "__utm1="+utmn+"."+utmu+"; path=/; expires=Sun, 18 Jan 2038 00:00:00 GMT"
    utm2 = "__utm2="+utmu+"; path=/; expires=Sun, 18 Jan 2038 00:00:00 GMT"
    utm3 = "__utm3="+utmu+"; path=/;"
    br.set_cookie(utm1)
    br.set_cookie(utm2)
    br.set_cookie(utm3)
    
    if TESTRUN: print 'Downloading and extracting CSV'
    try:
        tar_url = "https://www.broderbros.com/cgi-bin/download/webshr/prod-info-view.w?f=bro-AllStyles_R06.tar.gz"
        br.retrieve(tar_url, os.path.join(temp_dir, "bro-AllStyles_R06.tar.gz"))
        tar = tarfile.open(os.path.join(temp_dir, "bro-AllStyles_R06.tar.gz"))
        #~ member = tar.getmember('/usr/dbx/ai/AllStyles4/bro/items_R06.csv')   # get file info 
        for member in tar.getmembers():
            member.name = member.name.split('/')[-1]    # strip directory from filename
        tar.extractall(os.path.join(temp_dir, 'bro-AllStyles_R06'))
        tar.close()
    except:
        print "Issue in downloading CSV"
        return None
    
    #reader = csv.reader(open('data/bro-AllStyles_R06/items_R06.csv', 'rb'))
    
    f_object = open(os.path.join(temp_dir, 'bro-AllStyles_R06/items_R06.csv'), 'rb')
    reader = csv.reader(f_object)
    
    for row in reader:
        item_id = row[7].lower()
        if csv_output_dict.has_key(item_id):
            if TESTRUN:print "item id already in dictionary so excluding it."
            pass
        else:
            mill = row[23]
            item_url = 'https://www.broderbros.com/cgi-bin/online/webshr/prod-detail.w?sr='+str(item_id)
            browser = utils.create_browser(SLEEP_MIN, SLEEP_MAX)
            browser.set_handle_redirect(False)
            
            try:
                #~ browser.open_novisit(item_url)
                temp_dict = {}
                temp_dict['id'] = item_id.lower()
                temp_dict['brand'] = mill.lower()
                temp_dict['url'] = item_url
                csv_output_dict[item_id] = temp_dict
                if TESTRUN:
                    print temp_dict
                    print '+'*78
            except:
                pass
    f_object.close()
    shutil.rmtree(os.path.join(temp_dir, "bro-AllStyles_R06"))
    
    os.remove(os.path.join(temp_dir, "bro-AllStyles_R06.tar.gz"))
    return csv_output_dict


def get_stock_data():
    """ 
        Get item stock data from csv.
        Returns: { itemRef: [ {'options': [option_dict], 'price': [price_dict], 'inventory': int} ] }
        
        * option_dict = {'option_type': string, 'option_value': string, 'attributes': [attrib_dict]}
        ** attrib_dict = {'attribute_type': string, 'attribute_value': string}
        
        * price_dict = {'price_type': string, 'price': float, 'quantity_break_start': float, 'quantity_break_end': float}
        ** 'price_type', 'quantity_break_start' and 'quantity_break_end' are optional
        ** 'price', 'quantity_break_start', 'quantity_break_end' can be of any type that supported by decimal.Decimal()
    """
    if not os.path.exists('./catalog/stock_data'):
        os.mkdir('./catalog/stock_data')
    
    inventory_data = {}
    inventory_file = './catalog/stock_data/inventory-bro.txt'
    
    download_data = True
    if os.path.exists(inventory_file):
        # Check that inventory file is no more than 1 day old
        filestat = os.stat(inventory_file)
        tm = datetime.datetime.fromtimestamp(filestat.st_mtime)
        today = datetime.datetime.now()
        dt = today - tm
        if dt.days < 1:
            download_data = False
    
    if download_data:
        # Get inventory data from ftp site
        from ftplib import FTP_TLS
        print 'Downloading inventory-bro.txt ....'
        ftps = FTP_TLS('ftp.appareldownload.com')
        ftps.login('Br0d3r', 'Br0d3r2oll')
        ftps.prot_p()
        #ftps.retrlines('LIST')
        ftps.retrbinary('RETR inventory-bro.txt', open(inventory_file, 'wb').write)
        ftps.quit()
    
    print "Parse inventory-bro.txt ... "
    first_row = None
    for row in csv.reader(open(inventory_file, 'rb')):
        itemRef = row[4].lower()
        if itemRef == 'style number':
            # save first row to be used as column header
            first_row = row
            continue
        
        source_attribs = [{'attribute_type': 'source', 'attribute_value': 'broderbros'}]
        
        inventory_data.setdefault(itemRef, [])
        
        color = row[8].lower()
        size = row[10].lower()
        
        # Warehouses starts at column 13
        for i in range(13, len(first_row)):
            wh_name = first_row[i]
            options = [
                {'option_type': 'color', 'option_value': color, 'attributes': []},
                {'option_type': 'size', 'option_value': size, 'attributes': []},
                {'option_type': 'warehouse', 'option_value': wh_name, 'attributes': source_attribs, 'shared': True},
                {'option_type': 'vendor', 'option_value': 'broderbros', 'attributes': source_attribs, 'shared': True},
            ]
            inventory_data[itemRef].append({'options': options, 'inventory': row[i]})
    
    # Pricing data
    pricing_tarfile = "./catalog/stock_data/bro-AllStyles_R06.tar.gz"
    download_data = True
    if os.path.exists(pricing_tarfile):
        # Check that file is no more than 1 day old
        filestat = os.stat(pricing_tarfile)
        tm = datetime.datetime.fromtimestamp(filestat.st_mtime)
        today = datetime.datetime.now()
        dt = today - tm
        if dt.days < 1:
            download_data = False
    
    if download_data:
        print 'Downloading items.csv for price data ....'
        br = utils.create_browser(1, 2)
        br.open("https://www.broderbros.com/cgi-bin/online/webbro/bro-index.w")
        try:
            # Fill login form
            br.select_form(name = 'frmLogin')
            frm = br.form
            
            ctrl = frm.find_control('userName')
            ctrl.value = USERNAME
            ctrl = frm.find_control('password')
            ctrl.value = PASSWORD
            
            # Submit login form
            if TESTRUN: print 'Submit Login Form'
            
            br.select_form(name = 'frmLogin')
            br.submit()
        except:
            print "Login form does not exist, please check URL, downloaded html or site is down"
            return None
        try:
            tar_url = "https://www.broderbros.com/cgi-bin/download/webshr/prod-info-view.w?f=bro-AllStyles_R06.tar.gz"
            br.retrieve(tar_url, pricing_tarfile)
        except:
            print "Error when downloading pricing file"
            return None
    
    try:
        tar = tarfile.open(pricing_tarfile)
        for member in tar.getmembers():
            member.name = member.name.split('/')[-1]    # strip directory from filename
        tar.extractall('catalog/stock_data/bro-AllStyles_R06')
        tar.close()
    except:
        print "Error when extracting items.csv"
        return None
    
    f_object = open('./catalog/stock_data/bro-AllStyles_R06/items_R06.csv', 'rb')
    #~ f_object = open('items_R06.csv', 'rb')
    
    print "Parse items_R06.csv ... "
    for row in csv.reader(f_object):
        itemRef = row[7].lower()
        if itemRef == 'style code':
            continue
        
        size = row[8].lower()
        color = row[11].lower()
        price = row[18]
        
        item_data = inventory_data.get(itemRef)
        if not item_data:
            continue
        # Find data with same size and color
        for var_dict in item_data:
            options = var_dict['options']
            opt_dict = {}
            for opt in options:
                opt_type = opt['option_type']
                opt_value = opt['option_value']
                if opt_type == 'size':
                    opt_dict['size'] = opt_value
                elif opt_type == 'color':
                    opt_dict['color'] = opt_value
            if opt_dict['size'] == size and opt_dict['color'] == color:
                var_dict['price'] = [{'price_type': 'retail_price', 'price': price}]
    
    f_object.close()
    
    try:
        shutil.rmtree("./catalog/stock_data/bro-AllStyles_R06")
        #~ os.remove("./catalog/stock_data/bro-AllStyles_R06.tar.gz")
    except:
        pass
    
    return inventory_data



