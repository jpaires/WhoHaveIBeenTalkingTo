# -*- coding: utf-8 -*-
from services.emailLib import GmailAccount, SENT_TYPE_ID, RECEIVED_TYPE_ID
import mailbox

USER = "joao"
SENT_MAIL_FILE = "C:\Users\%s\AppData\Roaming\Thunderbird\Profiles\l5q2sj5x.default\ImapMail\imap.googlemail.com\[Gmail].sbd\Sent Mail" % USER
ALL_MAIL_FILE = "C:\Users\%s\AppData\Roaming\Thunderbird\Profiles\l5q2sj5x.default\ImapMail\imap.googlemail.com\[Gmail].sbd\All Mail" % USER

class ThunderbirdAccount(GmailAccount):
    
    def __init__(self, all_mail_file, sent_mail_file):
        
        self.__all_mail_file = all_mail_file
        self.__sent_mail_file = sent_mail_file
        
        self.__sent_mails = {}
        self._GmailAccount__archive = []
        self._GmailAccount__nums = []
        
        self._GmailAccount__email_processors = []
        
    def login(self, username, password):
        self._GmailAccount__username = username
        self._GmailAccount__password = password
        
        self.compute_contacts_list()
    
    def return_sent(self, email):
        return SENT_TYPE_ID
    
    def real_get_type(self, email):
        if email.id in self.__sent_mails:
            return SENT_TYPE_ID
        else:
            return RECEIVED_TYPE_ID
    
    def get_type(self, email):
        if email.id in self.__sent_mails:
            return SENT_TYPE_ID
        else:
            return RECEIVED_TYPE_ID
    
    def start_fetch_all(self):
        
        self.get_type = self.return_sent
        for msg_data in mailbox.mbox(self.__sent_mail_file):
            email = self.create_mail(msg_data)
            
            if email != None:
                self.__sent_mails[email.id] = email
                self._GmailAccount__archive.append(email)
        
        print "Sent emails done!"
        
        self.get_type = self.real_get_type
        for msg_data in mailbox.mbox(self.__all_mail_file):
            email = self.create_mail(msg_data)
            if email != None and (not (email.id in self.__sent_mails)):
                self._GmailAccount__archive.append(email)
        print "All emails done!"
        print "Total # of emails: %s" % self._GmailAccount__archive.__len__()

def main():
    sent_mail_file = SENT_MAIL_FILE
    all_mail_file = ALL_MAIL_FILE
    
    account = ThunderbirdAccount(all_mail_file, sent_mail_file)
    
    username = raw_input("Insert username:")
    password = raw_input("Insert password:")
    
    account.login(username, password)
    
    account.start_fetch_all()
    
    account.save()
  
if __name__ == "__main__":
    main() 
