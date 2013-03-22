# -*- coding: utf-8 -*-
import sys, os
from email.base64mime import header_encode
sys.path.append(os.getcwd() + "/services")

import imaplib
import re
import email
import time
import logging
from email.header import decode_header
from email.parser import Parser
import services.gdata.contacts.service

import cPickle as pickle

DEBUG_FLAG = False

DATA_FILE = "data.pkl"
NUMS_FILE = "nums.pkl"

RECEIVED_TYPE_ID = "received"
SENT_TYPE_ID = "sent"
DAILY_RECEIVED_TYPE_ID = "daily_received"
DAILY_SENT_TYPE_ID = "daily_sent"

class EmailManager():

    
    def __init__(self):
        self.__emails_timeline = {}
        self.__emails_count = 0
    
    def get_emails(self):
        return self.__emails_timeline
    
    def get_emails_count(self):
        return self.__emails_count
    
    emails_timeline = property(get_emails, None)
    emails_count = property(get_emails_count, None)
    
    def __create_year(self, year):
        self.__emails_timeline[year] = {}
    
    def __has_year(self, year):
        return year in self.__emails_timeline
    
    def __create_month(self, month, year):
        self.__emails_timeline[year][month] = {RECEIVED_TYPE_ID : {}, SENT_TYPE_ID : {}, DAILY_RECEIVED_TYPE_ID : {}, DAILY_SENT_TYPE_ID : {}}
    
    def __has_month(self, month, year):
        return self.__has_year(year) and month in self.__emails_timeline[year]
    
    def __create_day(self, day, month, year):
        self.__emails_timeline[year][month][DAILY_RECEIVED_TYPE_ID][day] = {}
        self.__emails_timeline[year][month][DAILY_SENT_TYPE_ID][day] = {}
    
    def __has_day(self, day, month, year):
        return self.__has_year(year) and self.__has_month(month, year) and day in self.__emails_timeline[year][month][DAILY_RECEIVED_TYPE_ID]
    
    def __insert_contact_in_month(self, contact, month, year, type):
        address = get_contact_address(contact)
        self.__emails_timeline[year][month][type][address] = []
    
    def __has_contact_in_month(self, contact, month, year, type):
        address = get_contact_address(contact)
        return self.__has_year(year) and self.__has_month(month, year) and address in self.__emails_timeline[year][month][type]
    
    def __get_contact_in_month(self, contact, month, year, type):
        address = get_contact_address(contact)
        return self.__emails_timeline[year][month][type][address]
    
    def __insert_email_in_sender(self, email, contact, month, year, type):
        address = get_contact_address(contact)
        self.__get_contact_in_month(address, month, year, type).append(email)
        
    def __insert_contact_in_day(self, contact, day, month, year, type):
        address = get_contact_address(contact)
        self.__emails_timeline[year][month][type][day][address] = []
    
    def __has_contact_in_day(self, contact, day, month, year, type):
        address = get_contact_address(contact)
        return self.__has_year(year) and self.__has_month(month, year) and self.__has_day(day, month, year) and address in self.__emails_timeline[year][month][type][day]
    
    def __get_contact_in_day(self, contact, day, month, year, type):
        address = get_contact_address(contact)
        return self.__emails_timeline[year][month][type][day][address]
    
    def __daily_insert_email_in_sender(self, email, contact,day, month, year, type):
        address = get_contact_address(contact)
        self.__get_contact_in_day(address, day, month, year, type).append(email)
    
    def __insert_email(self, email, year, month, day, type):
        if not self.__has_year(year):
            self.__create_year(year)
        if not self.__has_month(month, year):
            self.__create_month(month, year)
        if not self.__has_day(day, month, year):
            self.__create_day(day, month, year)
        
        if type == RECEIVED_TYPE_ID:
            contact = email.sender
            if not self.__has_contact_in_month(contact, month, year, type):
                self.__insert_contact_in_month(contact, month, year, type)
            if not self.__has_contact_in_day(contact, day, month, year, DAILY_RECEIVED_TYPE_ID):
                self.__insert_contact_in_day(contact, day, month, year, DAILY_RECEIVED_TYPE_ID)
            self.__insert_email_in_sender(email, contact, month, year, type)
            self.__daily_insert_email_in_sender(email, contact, day, month, year, DAILY_RECEIVED_TYPE_ID)
        elif type == SENT_TYPE_ID:
            for contact in email.recipient:
                if not self.__has_contact_in_month(contact, month, year, type):
                    self.__insert_contact_in_month(contact, month, year, type)
                if not self.__has_contact_in_day(contact, day, month, year, DAILY_SENT_TYPE_ID):
                    self.__insert_contact_in_day(contact, day, month, year, DAILY_SENT_TYPE_ID)
                self.__insert_email_in_sender(email, contact, month, year, type)
                self.__daily_insert_email_in_sender(email, contact, day, month, year, DAILY_SENT_TYPE_ID)
        
    def add_emails(self, emails):
        for email in emails:
            struct = time.localtime(email.time)
            self.__insert_email(email, struct.tm_year, struct.tm_mon, struct.tm_mday, email.type)
            
            self.__emails_count+=1

def get_contact_address(contact, is_correct_check = False):
    if "<" in contact:
        return contact[contact.index("<")+1:contact.index(">")]
    else:
        if not is_correct_check:
            return contact
        else:
            if "@" in contact:
                return contact
            else:
                return None

class Email_GVIP:
    """
        Represents an email. It hold the sender, the subject and the message.
        To access or modify these properties simply use '.sender', '.subject' and '.message' on the email instance.
    """
    def __init__(self, id = "", sender = "", recipient = "", subject = "", message = "", time = -1, type = RECEIVED_TYPE_ID):
        self.__id = id
        self.__sender = sender
        self.__recipient = recipient
        self.__subject = subject
        self.__message = message
        self.__time = time
        self.__type = type
    
    def get_id(self):
        return self.__id
    
    def set_id(self, new):
        self.__id= new
    
    def get_sender(self):
        return self.__sender
    
    def set_sender(self, new):
        self.__sender = new
    
    def get_recipient(self):
        return self.__recipient
    
    def set_recipient(self, new):
        self.__recipient = new
        
    def get_subject(self):
        return self.__subject
    
    def set_subject(self, new):
        self.__subject = new
        
    def get_message(self):
        return self.__message
    
    def set_message(self, new):
        self.__message = new
   
    def get_time(self):
        return self.__time
    
    def set_time(self, new):
        self.__time = new
    
    def get_type(self):
        return self.__type
    
    def set_type(self, new):
        self.__type = new
   
    def get_sender_address(self):
        if "<" in self.sender:
            return self.sender[self.sender.index("<")+1:self.sender.index(">")]
        else:
            return self.sender
    
    def get_recipient_address(self):
        if self.recipient is None:
            return None
        
        addresses = []
        for recipient in self.recipient:
            if "<" in recipient:
                addresses.append(recipient[recipient.index("<")+1:recipient.index(">")])
            else:
                addresses.append(recipient)
        
        return addresses
    
    id = property(get_id, set_id)
    sender = property(get_sender, set_sender)
    sender_address = property(get_sender_address, None)      
    recipient = property(get_recipient, set_recipient)
    recipient_address = property(get_recipient_address, None)
    subject = property(get_subject, set_subject)
    message = property(get_message, set_message)
    time = property(get_time, set_time)
    type = property(get_type, set_type)

class AllMailsLabelNotFoundException(Exception):
        def __init__(self, available_boxes):
            self.available_boxes = available_boxes
        def __str__(self):
            return repr(self.available_boxes)    
        
class SentMailsLabelNotFoundException(Exception):
        def __init__(self, available_boxes):
            self.available_boxes = available_boxes
        def __str__(self):
            return repr(self.available_boxes)     

class LanguageNotSupported(Exception):
    def __init__(self, available_boxes):
            self.available_boxes = available_boxes
            
    def __str__(self):
        return repr(self.available_boxes)

class WrongUsernameAndOrPasswordException(Exception):
    pass

class LoginException(Exception):
    def __init__(self, message):
        self.message = message
            
    def __str__(self):
        return repr(self.message)
    
class FetchException(Exception):
    def __init__(self, message):
        self.message = message
            
    def __str__(self):
        return repr(self.message)

class SearchException(Exception):
    def __init__(self, search_string):
        self.search_string = search_string
        
    def __str__(self):
        return repr(self.search_string)

class Contact:
        
        def __init__(self, name, emails = []):
            self.__name = name
            self.__emails = emails
            
        def get_name(self, safe = False):
            if safe and self.__name != None:
                return self.__name.replace("'", "\\'")
            return self.__name
        
        def get_safe_name(self):
            return self.get_name(safe = True)
        
        def get_emails(self):
            return self.__emails
    
        name = property(get_name, None)
        emails = property(get_emails, None)
        
        safe_name = property(get_safe_name, None)
 
class GmailAccount():
    
    def __init__(self, email_processors = []):
        self.__IMAP_SERVER='imap.gmail.com'
        self.__IMAP_PORT=993
        self.__M = None
        self.__response = None
        self.__selected = None
        
        self.__is_dirty = False
        
        try:
            pkl_file = open(DATA_FILE, 'rb')
            self.__fetched_mails = pickle.load(pkl_file)
            pkl_file.close()
        except IOError:
            self.__fetched_mails = []
            
        try:
            pkl_file = open(NUMS_FILE, 'rb')
            self.__nums = pickle.load(pkl_file)
            pkl_file.close()
        except IOError:
            self.__nums = None
            
        self.__archive = []
        
        if  email_processors.__class__ != [].__class__:
            self.__email_processors = [email_processors]
        else:
            self.__email_processors = email_processors
        for email in self.__fetched_mails:
            for email_processor in self.__email_processors:
                email_processor.process_email(email)    
    def get_response(self):
        return self.__id
    
    response = property(get_response, None)
    
    def reconnect(self):
        reconnected = False
        while not reconnected:
            if DEBUG_FLAG:
                logging.debug("reconnecting...")
            try:
                self.__M = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
                self.__Msent = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
        
                rc, self.response = self.__M.login(self.__username, self.__password)
                rc, self.response = self.__Msent.login(self.__username, self.__password)
            
                all_label = self.get_all_box_label()
                self.select_box(all_label)
            
                sent_label = self.get_sent_box_label()
                self.__Msent.select(sent_label)
            
                reconnected = True
                logging.debug("reconnected!")
            except:
                reconnected = False
                time.sleep(60)
        """    
        try:
            self.__M = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
            self.__Msent = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
        
            rc, self.response = self.__M.login(self.__username, self.__password)
            rc, self.response = self.__Msent.login(self.__username, self.__password)
            
            all_label = self.get_all_box_label()
            self.select_box(all_label)
            
            sent_label = self.get_sent_box_label()
            self.__Msent.select(sent_label)
            
            return True
        except:
            return False     
        """
        
    def login(self, username, password):
        """
            Performs the login with the give username and password. 
            Returns 'OK' if successful, the error message if not.
            IT MAY RAISE AN EXCEPTION.
        """
        try:
            self.__M = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
            self.__Msent = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
        except Exception as e:
            raise LoginException(e.message)
        
        try:
            rc, self.response = self.__M.login(username, password)
            rc, self.response = self.__Msent.login(username, password)
        except Exception as e:
            if "AUTHENTICATIONFAILED" in e.message:
                raise WrongUsernameAndOrPasswordException()
            raise LoginException(e.message)
        
        self.__username = username
        self.__password = password
        rc = self.__get_mailboxes()
        self.compute_contacts_list()
        
        
        if not "@gmail.com" in username:
            address = username + "@gmail.com"
        else:
            address = username
        
        try:
            sent_label = self.get_sent_box_label()
        except SentMailsLabelNotFoundException as e:
            raise LanguageNotSupported(e.available_boxes)
        
        self.__Msent.select(sent_label)
        
        return rc
 
    def get_contacts_list(self):
        return self.__contacts_list
    
    def get_contacts_mapping(self):
        return self.__contacts_mapping
 
    def compute_contacts_list(self):
        client = services.gdata.contacts.service.ContactsService()
        client.ClientLogin(self.__username, self.__password)
        contacts_feed = client.GetContactsFeed()
        
        self.__contacts_mapping = {}
        self.__contacts_list = []
        
        while(contacts_feed) :
            
            for entry in contacts_feed.entry:
                try:
                    emails = []
                    for email in entry.email:
                        emails.append(email.address)
                    contact = Contact(entry.title.text, emails)
                    for email in contact.emails:
                        self.__contacts_mapping[email] = contact
                    self.__contacts_list.append(contact)
                except:
                    continue
            ret = contacts_feed.GetNextLink()
            contacts_feed = client.GetContactsFeed(ret.href)  if(ret) else ret
    
    def is_a_contact(self, name):
        return name in self.__contacts_mapping
    
    def logout(self):
        self.__M.logout()
        
    def __get_mailboxes(self, only_name = True):
        rc, self.response = self.__M.list()
        self.__mailboxes = []
        for item in self.response:
            if not only_name:
                self.__mailboxes.append(item)
            else:
                name = item[item.index("/")+4:item.__len__()-1]
                self.__mailboxes.append(name)
                
        return self.__mailboxes
    
    def get_mailboxes(self):
        return self.__mailboxes
    
    SUPORTED_ALL_MAIL_LABELS = ['[Gmail]/All Mail',
                                '[Gmail]/Todo o correio',
                                '[Gmail]/Todos os e-mails']
    
    SUPORTED_SENT_MAIL_LABELS = ['[Gmail]/Sent Mail',
                                 '[Gmail]/Correio enviado',
                                 '[Gmail]/Todos os e-mails']
    
    def get_all_box_label(self):
        boxes = self.get_mailboxes()
        for suported_label in self.SUPORTED_ALL_MAIL_LABELS:
            if suported_label in boxes:
                return suported_label
        
        raise AllMailsLabelNotFoundException(boxes)
    
    def get_sent_box_label(self):
        boxes = self.get_mailboxes()
        for suported_label in self.SUPORTED_SENT_MAIL_LABELS:
            if suported_label in boxes:
                return suported_label
        
        raise SentMailsLabelNotFoundException(boxes)
    
    def select_box(self, box='Inbox', readonly='False'):
        rc, count = self.__M.select(box, readonly)
        self.__selected = box
        return rc, count
    
    def is_selected_box(self, box):
        return self.__selected is box
    
    def get_mail_count(self, box='Inbox'):
        rc, count = self.select_box(box)
        return count[0]

    def get_unread_count(self, box='Inbox'):
        rc, message = self.__M.status(box, "(UNSEEN)")
        unreadCount = re.search("UNSEEN (\d+)", message[0]).group(1)
        return unreadCount
    
    def get_type(self, email):
        try:
            count = self.__Msent.search(None, "((HEADER message-id " + email.id + "))")[1][0].split().__len__()
        except Exception as e:
            raise SearchException(e.message)
        if count == 0:
            return RECEIVED_TYPE_ID
        else:
            return SENT_TYPE_ID
    
    def __extract_field(self, raw_field):
        try:
            decode_field = decode_header(raw_field.replace("\r\n", ""))
            field = email.header.make_header(decode_field)
            return field.__unicode__().encode("utf-8")
        except UnicodeDecodeError as e:
            if DEBUG_FLAG:
                f = open("bug.txt", "a")
                f.write("%s\n" % e)
                f.write("raw_field : %s\n" % raw_field)
                f.write("---------------------\n")
                f.close()
            return decode_field[0][0]
        except AttributeError:
            return ""
    
    def get_mail(self, num, box='inbox', readonly=True):
        msg = self.fetch_mail(num, box, readonly)
        return self.create_mail(msg)
    
    def fetch_mail(self, num, box='inbox', readonly=True):
        if not self.is_selected_box(box):
            self.select_box(box, readonly)
            
        try:
            typ, msg_data = self.__M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (message-id from to cc bcc subject date)])')
        
            if(msg_data.__len__() == 1 and "Failure" in msg_data[0]):
                return None
            
            data = ""
            for field_index in range(1, msg_data[0].__len__()):
                data += msg_data[0][field_index]
            
            msg = Parser().parsestr(data)

            
            return msg
        except imaplib.IMAP4.abort as e:
            raise FetchException(e.message)
    
    def create_mail(self, msg):
        
        this_email = Email_GVIP()  
                    
        this_email.id = msg['message-id']
            
        # getting the sender            
        this_email.sender = self.__extract_field(msg['from'])
        sender_add = this_email.get_sender_address()

        type = self.get_type(this_email)
        
        if (type == RECEIVED_TYPE_ID and self.is_a_contact(sender_add)) or type == SENT_TYPE_ID:
            this_email.type = type
        else:
            return None
            
        # getting the recipient
        to = msg['to']
        cc = msg['cc']
        bcc = msg['bcc']
        recipients = []
            
        for recipient_field in [to, cc, bcc]:
            if recipient_field == None or recipient_field == "undisclosed-recipients:;":
                continue
                
            for recipient in recipient_field.replace("\r\n", "").split(",>"):
                if ("<" in recipient) and (not ">" in recipient):
                    recipient += ">"
                    
                recipient_name_and_address = self.__extract_field(recipient)
                recipient_add = get_contact_address(recipient_name_and_address)
                if self.is_a_contact(recipient_add) and recipient_name_and_address != None:
                    recipients += [recipient_name_and_address]
        """    
        if this_email.type == SENT_TYPE_ID:
            recipients = [value for value in recipients if not (get_contact_address(value) in self.__sender_addresses)]
        elif this_email.type == RECEIVED_TYPE_ID:
            recipients = [value for value in recipients if get_contact_address(value) in self.__sender_addresses]
            if not (str(self.__username + "@gmail.com") in recipients):
                recipients.append(self.__username + "@gmail.com")
        """    
        if recipients.__len__() > 0:
            this_email.recipient = recipients
        else:
            return None
                
            
        # getting the subject
        this_email.subject = self.__extract_field(msg['subject'])
            
        this_email.time = time.mktime(email.Utils.parsedate(msg['date']))

        for email_processor in self.__email_processors:
            email_processor.process_email(this_email)
        #self.process_tokens(this_email)
            
        return this_email
     
    def get_mail2(self, num, box='inbox', readonly=True):
        """
            Get a mail by its 'num', not its 'Message-id'
        """
        if not self.is_selected_box(box):
            self.select_box(box, readonly)
        
        this_email = Email_GVIP()
            
        try:
            typ, msg_data = self.__M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (message-id from to cc bcc subject date)])')
        
            if(msg_data.__len__() == 1 and "Failure" in msg_data[0]):
                return None
             
            data = ""
            for field_index in range(1, msg_data[0].__len__()):
                data += msg_data[0][field_index]
            
            msg = Parser().parsestr(data)
            
            this_email.id = msg['message-id'];
            
            # getting the sender            
            this_email.sender = self.__extract_field(msg['from'])
            sender_add = this_email.get_sender_address()
            
            """
            if self.is_this_user(sender_add):
                this_email.type = SENT_TYPE_ID
            elif self.__is_a_contact(sender_add):
                this_email.type = RECEIVED_TYPE_ID
            else:
                return None 
            """
            type = self.get_type(this_email)
            if (type == RECEIVED_TYPE_ID and self.is_a_contact(sender_add)) or type == SENT_TYPE_ID:
                this_email.type = type
            else:
                return None
            
            # getting the recipient
            to = msg['to']
            cc = msg['cc']
            bcc = msg['bcc']
            recipients = []
            
            for recipient_field in [to, cc, bcc]:
                if recipient_field == None or recipient_field == "undisclosed-recipients:;":
                    continue
                
                for recipient in recipient_field.replace("\r\n", "").split(",>"):
                    if ("<" in recipient) and (not ">" in recipient):
                        recipient += ">"
                    
                    recipient_name_and_address = self.__extract_field(recipient)
                    recipient_add = get_contact_address(recipient_name_and_address)
                    if self.is_a_contact(recipient_add) and recipient_name_and_address != None:
                        recipients += [recipient_name_and_address]
            
            if this_email.type == SENT_TYPE_ID:
                recipients = [value for value in recipients if not (get_contact_address(value) in self.__sender_addresses)]
            elif this_email.type == RECEIVED_TYPE_ID:
                recipients = [value for value in recipients if get_contact_address(value) in self.__sender_addresses]
                if not (str(self.__username + "@gmail.com") in recipients):
                    recipients.append(self.__username + "@gmail.com")
            
            if recipients.__len__() > 0:
                this_email.recipient = recipients
            else:
                return None
                
            
            # getting the subject
            this_email.subject = self.__extract_field(msg['subject'])
            
            this_email.time = time.mktime(email.Utils.parsedate(msg['date']))

            for email_processor in self.__email_processors:
                email_processor.process_email(this_email)
            #self.process_tokens(this_email)
            
            return this_email
        except imaplib.IMAP4.abort as e:
            raise FetchException(e.message)
        """
        except Exception, AttributeError:
            if DEBUG_FLAG:
                logging.debug("An error was occurred...");
                import traceback
                traceback.print_exc()
            return None
        """

    
    def __start_fetch_all(self):
        self.start_fetch_all()
        
    def __start_fetch(self, args):
        self.start_fetch(args)
    
    def start_fetch(self, box='inbox', criteria='ALL', oldest_first = False, asynchronous = False):
        if asynchronous:
            import threading
            th = threading.Thread(target = self.__start_fetch, args = (box, criteria, oldest_first))
            th.start()
        else:
            self.select_box(box, readonly=True)
            if self.__nums == None:
                try:
                    contacts = self.__contacts_mapping.keys()
                    search_str = "(" + " ".join(["OR" for contact in range(0, contacts.__len__() - 1)]) + " " + " ".join(["from %s" % contact for contact in contacts]) + ")"
                    typ, data = self.__M.search(None, search_str)
                    nums = data[0].split()
                except:
                    typ, data = self.__M.search(None, criteria)
                    nums = data[0].split()
                if oldest_first:
                    nums.sort(key=int, reverse=True)
                self.__nums = nums

            while self.__nums.__len__() > 0:
                num = self.__nums[self.__nums.__len__() -1]
                try:
                    mail = self.get_mail(num, box)
                except FetchException as e:
                    if DEBUG_FLAG:
                        f = open("fetchEx.txt", "a")
                        f.write(str(e) + "\n")
                        f.close()
                    self.reconnect()
                    logging.debug("restarting...\n")
                    continue
                except SearchException as e:
                    if DEBUG_FLAG:
                        f = open("fetchEx.txt", "a")
                        f.write(str(e) + "\n")
                        f.close()
                    self.reconnect()
                    logging.debug("restarting...\n")
                    continue
                except Exception as e:
                    mail = None
                    if DEBUG_FLAG:
                        f = open("emailLibEx.txt", "a")
                        f.write(str(e))
                        f.close()
                if mail != None:
                    self.__is_dirty = True
                    self.__fetched_mails.append(mail)
                self.__nums.pop()
            if DEBUG_FLAG:
                logging.debug("\n--------------------------------\n| Fetching process terminated! |\n--------------------------------\n")
            
            return self.__fetched_mails
    
    def start_fetch_all(self, asynchronous = False):
        try:
            all_mail_box = self.get_all_box_label()
        except AllMailsLabelNotFoundException as e:
            raise LanguageNotSupported(e.available_boxes)
        if asynchronous:
            import threading
            th = threading.Thread(target = self.__start_fetch_all)
            th.start()
        else:
            return self.start_fetch(box=all_mail_box) 
    
    def save(self):
        output = open(DATA_FILE, "wb")
        pickle.dump(self.__archive, output)
        output.close()
                        
        output = open(NUMS_FILE, "wb")
        pickle.dump(self.__nums, output)
        output.close()
        
    
    def get_emails(self):
        aux = self.__fetched_mails
        self.__archive += aux
        self.__fetched_mails = []
        if self.__is_dirty > 0:
            self.save();
        return aux
    
    def emails_to_fetch_count(self):
        if self.__nums is None:
            return None
        else:
            return self.__nums.__len__()
