def readtextfile():
    data_file = open('data.txt', 'rb')
    for line in data_file:
        print line

if __name__ == '__main__':
    readtextfile()