import urllib2
import re
import csv
output = open("Sample_data_dvlaregistrations.csv", "ab")
csv_writer = csv.writer(output)
#csv_writer.writerow(["Plate Number"])

def main():
    url = 'http://dvlaregistrations.direct.gov.uk/search/previous-auction-plates.html?plate=3&searched=true&x=-233&y=-541'
    html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    find_all_plate_div = re.findall(r'<div class="resultsstripplate">.*?</div>', html_response)
    
    for all_div in find_all_plate_div:
        find_all_img = re.findall(r'title="(.*?)"', all_div)
        csv_writer.writerow(["".join(find_all_img)])
        print '*'*78
    
if __name__ == "__main__":
    main()