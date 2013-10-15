#http://segfault.in/2010/07/playing-with-python-and-gmail-part-1/

import imaplib
import re
 
class pygmail:
    def __init__(self):
        self.IMAP_SERVER='imap.gmail.com'
        self.IMAP_PORT=993
        self.M = None
        self.response = None
        self.mailboxes = []
 
    def login(self, username, password):
        self.M = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
        rc, self.response = self.M.login(username, password)
        return rc
    
    def get_mailboxes(self):
        rc, self.response = self.M.list()
        for item in self.response:
#            print item
            self.mailboxes.append(item.split()[-1])
        return rc
    
    def get_mail_count(self, folder='Inbox'):
        rc, count = self.M.select(folder)
        return count[0]
    
    def get_unread_count(self, folder='Inbox'):
        rc, message = self.M.status(folder, "(UNSEEN)")
        unreadCount = re.search("UNSEEN (\d+)", message[0]).group(1)
        return unreadCount
 
    def logout(self):
        self.M.logout()
        
if __name__ == '__main__':
    g = pygmail()
    g.login('satyandrab@gmail.com', '###chand321')
    print g.response
    
#    g.get_mailboxes()
#    for item in g.mailboxes:
#        print item
    
    total_mails = g.get_mail_count('inbox')
    print total_mails
    
    unread = g.get_unread_count('inbox')
    print unread