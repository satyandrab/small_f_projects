#http://segfault.in/2010/07/playing-with-python-and-gmail-part-1/

import imaplib
import re
 
class pygmail:
    
    _res = [
                r'\s(http://[^\s]+\.\w+/members/earn.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/plg_earn_mail_credit_frame.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/refmail.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/gotlinks_V2.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/randommail.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/[^s]+solo.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/[^s]+network.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/sesuper.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/ladyrose.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/credit_click.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/[^s]+clicks.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/ngetcredits.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/[^s]+ads.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/pinnacle.php\?.*?)\s',
                r'\s(http://[^\s]+\.\w+/soload.php\?.*?)\s'
            ]
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
            print item
            self.mailboxes.append(item.split()[-1])
        return rc
    
    def get_mail_count(self, folder='Inbox'):
        rc, count = self.M.select(folder)
        print count
        return count[0]
    
    def get_unread_count(self, folder='Inbox'):
        rc, message = self.M.status(folder, "(UNSEEN)")
        unreadCount = re.search("UNSEEN (\d+)", message[0]).group(1)
        return unreadCount
    
    def read_mails(self, folder='INBOX', mails=0):
        self.M.select(folder)
        result, data = self.M.uid('search', None, "UNSEEN") # search and return uids instead
        links = []
        if mails == 0:
            for uid in data[0].split():
                result, data = self.M.uid('fetch', uid, '(RFC822)')
                raw_email = data[0][1]
                self.M.store(uid, '+FLAGS', 'SEEN')
                for re_patt in self._res:
                    link = re.findall(re_patt, " ".join(raw_email.split()))
                    if link:
                        links.append(link[0])
                    break
                else:
                    print "No email pattern found in mail"
        else:
            for uid in data[0].split()[len(data[0].split())-mails:]:
                result, data = self.M.uid('fetch', uid, '(RFC822)')
                raw_email = data[0][1]
                self.M.store(uid, '+FLAGS', 'SEEN')
                link = re.findall(" (http://igot-mails\.com/credit_click.php.*?) "," ".join(raw_email.split()))
                if link:
                    links.append(link[0])
        return links
 
    def logout(self):
        self.M.logout()
        
#if __name__ == '__main__':
#    g = pygmail()
#    username = sys.argv[0]
#    passw = sys.argv[1]
#    folder = sys.argv[2]
#    mails = int(sys.argv[3])
##    mails = 10
#    
#    username = "satyandrab@gmail.com"
#    passw = "###chand321"
#    g.login(username, passw)
#    folder = "igot"
#    unread = g.get_unread_count(folder)
#    if unread == 0:
#        break
#    if mails > unread:
#        print "There are only ", unread,"unread mails in label", folder
#        g.read_mails(folder)
#    else:
#    g.read_mails(folder, mails)
#    g.get_mail_count(folder)
#    g.get_mailboxes()
        
#    for item in g.get_mailboxes:
#        print item
    
#    total_mails = g.get_mail_count('igot')
#    print total_mails
    
    
#    print unread