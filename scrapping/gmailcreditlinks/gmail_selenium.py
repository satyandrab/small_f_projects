from selenium import webdriver
import time
import sys, getpass
from readmail import pygmail

def close_windows(driver):
    close_windows = """
             var r = confirm("Close all other windows?");
             alert(r);
            """
    driver.execute_script(close_windows)
    
    while True:
        try:
            text1 = driver.switch_to_alert().text
            if text1 in ('Close all other windows?',):
                time.sleep(2)
                continue
            else:
                close = driver.switch_to_alert()
                result = close.text
                close.accept()
                break
                
        except:
            pass
    return result

def open_links(driver, label, mails, secs):
    g = pygmail()
    g.login(username, password)
    unread = g.get_unread_count(label)
    print "total unread mails are ->",str(int(unread)-2)
    
    if unread == 0:
        driver.execute_script("alert('There are no more unread mails in this label. Moving to next label if any.')")
        time.sleep(3)
        driver.switch_to_alert().accept()
        return "false"
    if mails > unread:
        print "There are only ", unread,"unread mails in label", label
        links = g.read_mails(label)
    else:
        links = g.read_mails(label, mails)
    
    driver_instances = []
    for link in links:
        driver_ins = webdriver.Firefox()
        driver_instances.append(driver_ins)
        driver_ins.get(link)
        driver_ins.maximize_window()
    
    time.sleep(secs)
    
    close = close_windows(driver)
    while True:
        print "Calling close windows"
        print type(close), close
        if close == "false":
            driver.execute_script("alert('Waiting for 10 secs and will ask you again to close windows');")
            time.sleep(4)
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            time.sleep(10)
            close = close_windows(driver)
        elif close == "true":
            for ins in driver_instances:
                ins.quit()
            break
    
    
    more_mails = """
             var r = confirm("Show more mails?");
             alert(r);
            """
    driver.execute_script(more_mails)
    
    while True:
        try:
            text1 = driver.switch_to_alert().text
            if text1 in ('Show more mails?',):
                time.sleep(3)
                print '1'
                continue
            else:
                mails = driver.switch_to_alert()
                print "more mails yes or no"
                result = mails.text
                mails.accept()
                break
                
        except Exception as e:
            print e
    return result
    
    
username = raw_input("Please enter your gmail username: ")
password = getpass.getpass("Please enter password for your account: ")
#username = "satyandrab@gmail.com"
#password = "###chand321"
number_of_folders = raw_input("How many labels you want to open?  ")
labels = []
data = {}
try:
    number_labels = int(number_of_folders)
except:
    print "Please enter only integer(1,2,3...)"

print "i'm going to ask you label names and their specification",
print number_labels,
print " times"
for i in range(number_labels):
    label = "_".join(raw_input("Please enter label name:  ").split())
    message = "Please enter number(Integer) of mails to open at a time for "+label+"  "
    try:
        mails_to_open = int(raw_input(message))
    except:
        print "Please enter only integer(1,2,3...)"
        sys.exit(-1)
    message = "For how much seconds you want to open a mail for "+label+"?  "
    try:
        time_op = int(raw_input(message))
    except:
        print "Please enter only integer(1,2,3...)"
        sys.exit(-1)
    data[label] = {}
    data[label]['mails'] = mails_to_open
    data[label]['time'] = time_op

driver = webdriver.Firefox()
driver.get("http://mail.google.com/")
driver.find_element_by_id("Email").clear()
driver.find_element_by_id("Email").send_keys(username)

driver.find_element_by_id("Passwd").clear()
driver.find_element_by_id("Passwd").send_keys(password)
if not driver.find_element_by_id("PersistentCookie").is_selected():
    driver.find_element_by_id("PersistentCookie").click()
driver.find_element_by_id("signIn").click()

driver.maximize_window()
time.sleep(30)
labels_read = data.keys()
for label_wu in labels_read:
    
    label = " ".join(label_wu.split('_'))
    try:
        search_text = "label:"+label
        driver.find_element_by_id("gbqfq").clear()
        driver.find_element_by_id("gbqfq").send_keys()
        
        driver.find_element_by_id("gbqfb").click()
    except:
        try:
            driver.find_element_by_id("gbqfq").clear()
            driver.find_element_by_id("gbqfq").send_keys()
            
            driver.find_element_by_id("gbqfb").click()
        except:
            print "Couldn't find search box."
    
    mails = data[label_wu]['mails']
    
    try:
        search_text = "label:"+label
        driver.find_element_by_id("gbqfq").clear()
        driver.find_element_by_id("gbqfq").send_keys()
        
        driver.find_element_by_id("gbqfb").click()
    except:
        try:
            driver.find_element_by_id("gbqfq").clear()
            driver.find_element_by_id("gbqfq").send_keys()
            
            driver.find_element_by_id("gbqfb").click()
        except:
            print "Couldn't find search box."
    
    while True:
        same_label = open_links(driver, label, mails, data[label_wu]['time'])
        if same_label == 'true':
            continue
        else:
            break

driver.execute_script("alert('All process done. It will exit now.');")
time.sleep(2)
try:
    driver.switch_to_alert().accept()
except:
    pass
time.sleep(5)
driver.quit()