'''
Created on Aug 21, 2013

@author: satyandra.babu
'''
import re
from collections import Counter
def main():
    number_of_string = 0
    sample_file = open('sample.txt', 'rb')
    date_list = []
    name_list = []
    attachment_list = []
    for line in sample_file:
        number_of_string = number_of_string+1
        find_data = re.findall(r'(.*?) (.*?):(.*?):(.*?): (.*?): (.*)', line)
        date = find_data[0][0]
        if date == '16-05-13':
            print 'Yes'
            print date
            date_list.append(line)
        name = find_data[0][4]
        attachment = find_data[0][5]
        if '<attached>' in attachment:
            attachment = attachment.replace('<attached>', '').replace('\r', '').strip()
            attachment_list.append(attachment)
        name_list.append(name)
        print name_list
        print '='*78
        
    print "Number of string :- "+str(number_of_string)
    print Counter(name_list)
    print "Number of attachments :- "+str(len(attachment_list))
    print "Attachments :- "+str(attachment_list)
    print "conversation for particular date in sample its, 16-05-13"
    print '*'*78
    for line in date_list:
        print line
    print '*'*78
        

if __name__ == '__main__':
    main()