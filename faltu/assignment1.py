'''
Created on Aug 19, 2013

@author: satyandra.babu
'''

def main():
    for number in range(50, 501):
        if int(number)%5 == 0 and int(number)%11 == 0:
            print 'Awesome'
        elif int(number)%5 == 0:
            print 'Python'
        elif int(number)%11 == 0:
            print 'Django'
        else:
            print number

if __name__ == '__main__':
    main()