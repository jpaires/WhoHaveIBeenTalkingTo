# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

import math, calendar, time

from services.tokenizer import Tokenize

from emailLib import RECEIVED_TYPE_ID, SENT_TYPE_ID, DAILY_RECEIVED_TYPE_ID, DAILY_SENT_TYPE_ID, get_contact_address

THEME_PATH = "theme"
INDEX_FILE_PATH = "%s/%s" % (THEME_PATH, "index.html")
LOGIN_FILE_PATH = "%s/%s" % (THEME_PATH, "login.html")
LANGUAGE_NOT_SUPPORTED_FILE_PATH = "%s/%s" % (THEME_PATH, "language-not-supported.html")
OOPS_FILE_PATH = "%s/%s" % (THEME_PATH, "oops.html")

def get_days_of_the_month(month, year):
    return calendar.monthrange(year, month)[1]
    

class Theme:
    def __init__(self):
        pass
    
    def __get_emails_tokens(self, emails):
        words = []
        for email in emails:
            tokens = Tokenize(email.subject)
            #tokens += Tokenize(email.message)
            for token in tokens:
                if not (token in words):
                    words.append(token)
        return words
    
    def __get_timelines_str(self, timeline, contacts_mapping, type, max_montly_email_count, max_daily_email_count):
        if type == RECEIVED_TYPE_ID:
            daily_type = DAILY_RECEIVED_TYPE_ID
        else:
            daily_type = DAILY_SENT_TYPE_ID
    
        daily_timeline_data = "["
        timeline_data = "["
        minyear = 0
        for year in timeline:
            if minyear == 0:
                min_month = min(timeline[year].keys())
                minyear = year
            else:
                min_month = 1
            if year == max(timeline.keys()):
                max_month = max(timeline[year].keys())
            else:
                max_month = 12
            months = []
            i = min_month
            while i <= max_month:
                months.append(i)
                i += 1
            timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            daily_timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            for month in months:
                if month in timeline[year]:
                    daily_timeline_data += "\t[\n"
                    for day in range(1, get_days_of_the_month(month, year) + 1):
                        if day in timeline[year][month][daily_type]:
                            daily_timeline_data += "\t\t[\n"
                            data = []
                            for sender in timeline[year][month][daily_type][day]:
                                words = self.__get_emails_tokens(timeline[year][month][type][sender])
                                    
                                    
                                count = timeline[year][month][daily_type][day][sender].__len__()
                                value = math.log(count+1, max_daily_email_count)
                                
                                try:
                                    name = contacts_mapping[sender].safe_name
                                except KeyError:
                                    continue
                                if name != None:
                                    name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                                else:
                                    name_and_sender = sender
                                data.append([value, count ,name_and_sender, words])
                            data.sort(key= lambda k: k[0], reverse = True)
                            sender_index = 0
                            while sender_index < data.__len__():
                                names = "'%s'," % (data[sender_index][2])
                                current_value = data[sender_index][0]
                                current_count = data[sender_index][1]
                                words_string = "[" + ", ".join(["'%s'" % (word) for word in data[sender_index][3]]) + "]"
                                words = "%s, " % words_string
                                more_sender_index = sender_index + 1
                                while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                                    names += "'" + data[more_sender_index][2] + "',"
                                    words_string = "[" + ", ".join(["'%s'" % (word) for word in data[more_sender_index][3]]) + "]"    
                                    words += "%s, " % words_string
                                    more_sender_index += 1
                                daily_timeline_data += "\t\t\t{value:%s, count:%s,name:[%s], words:[%s]},\n" % ( current_value, current_count, names, words)
                                sender_index = more_sender_index
                            daily_timeline_data += "\t\t],\n"
                        else:
                            daily_timeline_data += "\t\t[],\n"
                    daily_timeline_data += "\t],\n"
                    timeline_data += "\t[\n"
                    data = []
                    for sender in timeline[year][month][type]:
                        words = self.__get_emails_tokens(timeline[year][month][type][sender])
                        count = timeline[year][month][type][sender].__len__()
                        value = math.log(count+1, max_montly_email_count)
                        
                        try:
                            name = contacts_mapping[sender].safe_name
                        except KeyError:
                            continue
                        if name != None:
                            name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                        else:
                            name_and_sender = sender
                        data.append([value, count ,name_and_sender, words])
                    data.sort(key= lambda k: k[0], reverse = True)
                    sender_index = 0
                    while sender_index < data.__len__():
                        names = "'%s', " % (data[sender_index][2])
                        current_value = data[sender_index][0]
                        current_count = data[sender_index][1]
                        words_string = "[" + ", ".join(["'%s'" % (word) for word in data[sender_index][3]]) + "]"
                        words = "%s, " % words_string
                        more_sender_index = sender_index + 1
                        while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                            names += "'" + data[more_sender_index][2] + "',"
                            words_string = "[" + ", ".join(["'%s'" % (word) for word in data[more_sender_index][3]]) + "]"    
                            words += "%s, " % words_string
                            more_sender_index += 1
                        timeline_data += "\t\t{value:%s, count:%s,name:[%s], words:[%s]},\n" % ( current_value, current_count, names, words)
                        sender_index = more_sender_index    
                    timeline_data += "\t],\n"
                else:
                    timeline_data += "\t[],\n"
                    daily_timeline_data += "\t[\n"
                    for j in range(1, get_days_of_the_month(month, year) + 1):
                        daily_timeline_data += "\t\t[],\n"
                    daily_timeline_data += "\t],\n"
            timeline_data += "]},\n"
            daily_timeline_data += "]},\n"
        timeline_data += "]\n"
        daily_timeline_data += "]\n"
        
        return timeline_data, daily_timeline_data
    
    def get_index_html(self, still_to_fetch_count = None, email_manager = None, timeline = None, contacts_mapping = None, contacts_object_list = None, key_words_manager = None):
        if still_to_fetch_count == None and email_manager == None and timeline == None and contacts_mapping == None and contacts_object_list == None and key_words_manager == None:
            return self.get_from_file(INDEX_FILE_PATH) % ("[]", "{}", "", "{}", "{}", "{}", "{}", "{}", "[]")
        
        init = time.time()
        
        contacts_list = []
        
        max_montly_email_count = 0
        max_daily_email_count = 0
        for year in timeline:
            for month in timeline[year]:
                
                for sender in timeline[year][month][RECEIVED_TYPE_ID]:
                    try:
                        name = contacts_mapping[sender].safe_name
                    except KeyError:
                        continue
                    if name != None:
                        name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                    else:
                        name_and_sender = sender
                    if not name_and_sender in contacts_list:
                        contacts_list.append(name_and_sender)
                    current = timeline[year][month][RECEIVED_TYPE_ID][sender].__len__()
                    if current > max_montly_email_count:
                        max_montly_email_count = current
                
                for recipient in timeline[year][month][SENT_TYPE_ID]:
                    current = timeline[year][month][SENT_TYPE_ID][recipient].__len__()
                    if current > max_montly_email_count:
                        max_montly_email_count = current
                        
                for day in timeline[year][month][DAILY_RECEIVED_TYPE_ID]:
                    for sender in timeline[year][month][DAILY_RECEIVED_TYPE_ID][day]:
                        current = timeline[year][month][DAILY_RECEIVED_TYPE_ID][day][sender].__len__()
                        if current > max_daily_email_count:
                            max_daily_email_count = current
                                    
                for day in timeline[year][month][DAILY_SENT_TYPE_ID]:
                    for recipient in timeline[year][month][DAILY_SENT_TYPE_ID][day]:
                        current = timeline[year][month][DAILY_SENT_TYPE_ID][day][recipient].__len__()
                        if current > max_daily_email_count:
                            max_daily_email_count = current
        
        if max_montly_email_count == 1:
            max_montly_email_count = 2
        
        if max_daily_email_count == 1:
            max_daily_email_count = 2
        
        contacts_to_keywords_mapping = "{" 
        for sender in contacts_list:
            contacts_to_keywords_mapping += "'%s' : " % (get_contact_address(sender))
            contacts_to_keywords_mapping += "["
            top_keywords = key_words_manager.get_contact_top_keywords(sender)
            for keyword, val in top_keywords:
                contacts_to_keywords_mapping += "{text: '%s', weight: %s}," % (str(keyword), str(val))
            contacts_to_keywords_mapping += "],"
        contacts_to_keywords_mapping += "}"
        
        contact_name_to_emails = "{"
        contacts_list_str = "["
        for contact in contacts_object_list:
            if contact.safe_name != None:
                contacts_list_str += "'%s', " % (contact.safe_name)
                contact_name_to_emails += "'%s':[" % (contact.safe_name)
                for email in contact.emails:
                    contacts_list_str += "'%s', " % (email)
                    contact_name_to_emails += "'%s'," % (email)
                contact_name_to_emails += "],"
            else:
                for email in contact.emails:
                    contacts_list_str += "'%s', " % (email)
        contacts_list_str += "]"
        contact_name_to_emails += "}"
        
        init2 = time.time()
        received_timeline_data, daily_received_timeline_data = self.__get_timelines_str(timeline, contacts_mapping, RECEIVED_TYPE_ID, max_montly_email_count, max_daily_email_count)
        
        sent_timeline_data, daily_sent_timeline_data = self.__get_timelines_str(timeline, contacts_mapping, SENT_TYPE_ID, max_montly_email_count, max_daily_email_count)
            
        cloud_data = "["
        for token, value in key_words_manager.top_keywords:
            cloud_data += "{text: '%s', weight: %s}," % (str(token), value)
        cloud_data += "]"
        
        
        if still_to_fetch_count == 0:
            fetched_str = "All (%s) emails indexed" % (email_manager.get_emails_count())
        elif still_to_fetch_count is None:
            fetched_str = ""
        else:
            fetched_str = "%s emails indexed" % (email_manager.get_emails_count())
        
        return self.get_from_file(INDEX_FILE_PATH) % (contacts_list_str, contact_name_to_emails, fetched_str, received_timeline_data, sent_timeline_data, contacts_to_keywords_mapping, daily_received_timeline_data, daily_sent_timeline_data, cloud_data)
    
    """
    def get_index_html2(self, email_account, timeline, contacts_mapping, key_words_manager):
        
        init = time.time()
        
        contacts_list = []
        max_montly_email_count = 0
        max_daily_email_count = 0
        for year in timeline:
            for month in timeline[year]:
                for sender in timeline[year][month][RECEIVED_TYPE_ID]:
                    name = contacts_mapping[sender]
                    if name != None:
                        name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                    else:
                        name_and_sender = sender
                    if not name_and_sender in contacts_list:
                        contacts_list.append(name_and_sender)
                    current = timeline[year][month][RECEIVED_TYPE_ID][sender].__len__()
                    if current > max_montly_email_count:
                        max_montly_email_count = current
                
                for recipient in timeline[year][month][SENT_TYPE_ID]:
                    current = timeline[year][month][SENT_TYPE_ID][recipient].__len__()
                    if current > max_montly_email_count:
                        max_montly_email_count = current
                        
                for day in timeline[year][month][DAILY_RECEIVED_TYPE_ID]:
                    for sender in timeline[year][month][DAILY_RECEIVED_TYPE_ID][day]:
                        current = timeline[year][month][DAILY_RECEIVED_TYPE_ID][day][sender].__len__()
                        if current > max_daily_email_count:
                            max_daily_email_count = current
                                    
                for day in timeline[year][month][DAILY_SENT_TYPE_ID]:
                    for recipient in timeline[year][month][DAILY_SENT_TYPE_ID][day]:
                        current = timeline[year][month][DAILY_SENT_TYPE_ID][day][recipient].__len__()
                        if current > max_daily_email_count:
                            max_daily_email_count = current
        
        contacts_list_str = "["
        contacts_to_keywords_mapping = "{" 
        for sender in contacts_list:
            contacts_list_str += "'%s' ," % (sender)
            contacts_to_keywords_mapping += "'%s' : " % (get_contact_address(sender))
            contacts_to_keywords_mapping += "["
            top_keywords = key_words_manager.get_contact_top_keywords(sender)
            for keyword, val in top_keywords:
                contacts_to_keywords_mapping += "{text: '%s', weight: %s}," % (str(keyword), str(val))
            contacts_to_keywords_mapping += "],"
        contacts_list_str += "]"
        contacts_to_keywords_mapping += "}"
        
        
        init2 = time.time()
        daily_received_timeline_data = "["
        received_timeline_data = "["
        minyear = 0
        for year in timeline:
            if minyear == 0:
                min_month = min(timeline[year].keys())
                minyear = year
            else:
                min_month = 1
            if year == max(timeline.keys()):
                max_month = max(timeline[year].keys())
            else:
                max_month = 12#max(timeline[year].keys())
            months = []
            i = min_month
            while i <= max_month:
                months.append(i)
                i += 1
            received_timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            daily_received_timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            for month in months:
                if month in timeline[year]:
                    daily_received_timeline_data += "\t[\n"
                    for day in range(1, get_days_of_the_month(month, year) + 1):
                        if day in timeline[year][month][DAILY_RECEIVED_TYPE_ID]:
                            daily_received_timeline_data += "\t\t[\n"
                            data = []
                            for sender in timeline[year][month][DAILY_RECEIVED_TYPE_ID][day]:
                                count = timeline[year][month][DAILY_RECEIVED_TYPE_ID][day][sender].__len__()
                                #value = float(count)/float(max_montly_email_count)
                                value = math.log(count+1, max_daily_email_count)
                                
                                name = contacts_mapping[sender]
                                if name != None:
                                    name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                                else:
                                    name_and_sender = sender
                                data.append([value, count ,name_and_sender])
                            data.sort(key= lambda k: k[0], reverse = True)
                            sender_index = 0
                            while sender_index < data.__len__():
                                names = "'%s'," % (data[sender_index][2])
                                current_value = data[sender_index][0]
                                current_count = data[sender_index][1]
                                more_sender_index = sender_index + 1
                                while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                                    names += "'" + data[more_sender_index][2] + "',"
                                    more_sender_index += 1
                                daily_received_timeline_data += "\t\t\t{value:%s, count:%s,name:[%s]},\n" % ( current_value, current_count, names)
                                sender_index = more_sender_index
                            daily_received_timeline_data += "\t\t],\n"
                        else:
                            daily_received_timeline_data += "\t\t[],\n"
                    daily_received_timeline_data += "\t],\n"
                    received_timeline_data += "\t[\n"
                    data = []
                    for sender in timeline[year][month][RECEIVED_TYPE_ID]:
                        words = []
                        for email in timeline[year][month][RECEIVED_TYPE_ID][sender]:
                            tokens = Tokenize(email.subject)
                            for token in tokens:
                                address = get_contact_address(sender)
                            tokens += Tokenize(email.message)
                            for token in tokens:
                                if not (token in words):
                                    words.append(token)
                        
                        count = timeline[year][month][RECEIVED_TYPE_ID][sender].__len__()
                        #value = float(count)/float(max_montly_email_count)
                        value = math.log(count+1, max_montly_email_count)
                        
                        name = contacts_mapping[sender]
                        if name != None:
                            name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                        else:
                            name_and_sender = sender
                        data.append([value, count ,name_and_sender, words])
                    data.sort(key= lambda k: k[0], reverse = True)
                    sender_index = 0
                    while sender_index < data.__len__():
                        names = "'%s', " % (data[sender_index][2])
                        current_value = data[sender_index][0]
                        current_count = data[sender_index][1]
                        words_string = "[" + ", ".join(["'%s'" % (word) for word in data[sender_index][3]]) + "]"
                        words = "%s, " % words_string
                        more_sender_index = sender_index + 1
                        while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                            names += "'" + data[more_sender_index][2] + "',"
                            words_string = "[" + ", ".join(["'%s'" % (word) for word in data[more_sender_index][3]]) + "]"    
                            words += "%s, " % words_string
                            more_sender_index += 1
                        received_timeline_data += "\t\t{value:%s, count:%s,name:[%s], words:[%s]},\n" % ( current_value, current_count, names, words)
                        sender_index = more_sender_index    
                    received_timeline_data += "\t],\n"
                else:
                    received_timeline_data += "\t[],\n"
                    daily_received_timeline_data += "\t[\n"
                    for j in range(1, get_days_of_the_month(month, year) + 1):
                        daily_received_timeline_data += "\t\t[],\n"
                    daily_received_timeline_data += "\t],\n"
            received_timeline_data += "]},\n"
            daily_received_timeline_data += "]},\n"
        received_timeline_data += "]\n"
        daily_received_timeline_data += "]\n"
        
        sent_timeline_data = "["
        daily_sent_timeline_data = "["
        minyear = 0
        for year in timeline:
            if minyear == 0:
                min_month = min(timeline[year].keys())
                minyear = year
            else:
                min_month = 1
            max_month = 12#max(timeline[year].keys())
            months = []
            i = min_month
            while i <= max_month:
                months.append(i)
                i += 1
            sent_timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            daily_sent_timeline_data += "{ year:%s, minMonth:%s, months:[\n" % (year, min_month)
            for month in months:
                if month in timeline[year]:
                    daily_sent_timeline_data += "\t[\n"
                    for day in range(1, get_days_of_the_month(month, year) + 1):
                        if day in timeline[year][month][DAILY_SENT_TYPE_ID]:
                            daily_sent_timeline_data += "\t\t[\n"
                            data = []
                            for sender in timeline[year][month][DAILY_SENT_TYPE_ID][day]:
                                count = timeline[year][month][DAILY_SENT_TYPE_ID][day][sender].__len__()
                                #value = float(count)/float(max_montly_email_count)
                                value = math.log(count+1, max_daily_email_count)
                                
                                name = contacts_mapping[sender]
                                if name != None:
                                    name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                                else:
                                    name_and_sender = sender
                                data.append([value, count ,name_and_sender])
                            data.sort(key= lambda k: k[0], reverse = True)
                            sender_index = 0
                            while sender_index < data.__len__():
                                names = "'%s'," % (data[sender_index][2])
                                current_value = data[sender_index][0]
                                current_count = data[sender_index][1]
                                more_sender_index = sender_index + 1
                                while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                                    names += "'" + data[more_sender_index][2] + "',"
                                    more_sender_index += 1
                                daily_sent_timeline_data += "\t\t\t{value:%s, count:%s,name:[%s]},\n" % ( current_value, current_count, names)
                                sender_index = more_sender_index
                            daily_sent_timeline_data += "\t\t],\n"
                        else:
                            daily_sent_timeline_data += "\t\t[],\n"
                    daily_sent_timeline_data += "\t],\n"
                    sent_timeline_data += "\t[\n"
                    data = []
                    for sender in timeline[year][month][SENT_TYPE_ID]:
                        words = []
                        for email in timeline[year][month][SENT_TYPE_ID][sender]:
                            tokens = Tokenize(email.subject)
                            for token in tokens:
                                address = get_contact_address(sender)
                            tokens += Tokenize(email.message)
                            for token in tokens:
                                if not (token in words):
                                    words.append(token)
                        count = timeline[year][month][SENT_TYPE_ID][sender].__len__()
                        #value = float(count)/float(max_montly_email_count)
                        value = math.log(count+1, max_montly_email_count)
                        name = contacts_mapping[sender]
                        if name != None:
                            name_and_sender = "%s <%s>" % (name.replace("'", ""), sender)
                        else:
                            name_and_sender = sender
                        data.append([value, count ,name_and_sender, words])
                    data.sort(key= lambda k: k[0], reverse = True)
                    sender_index = 0
                    while sender_index < data.__len__():
                        names = "'%s'," % (data[sender_index][2])
                        current_value = data[sender_index][0]
                        current_count = data[sender_index][1]
                        words_string = "[" + ", ".join(["'%s'" % (word) for word in data[sender_index][3]]) + "]"
                        words = "%s, " % words_string
                        more_sender_index = sender_index + 1
                        while more_sender_index < data.__len__() and data[more_sender_index][1] == current_count:
                            names += "'" + data[more_sender_index][2] + "',"
                            words_string = "[" + ", ".join(["'%s'" % (word) for word in data[more_sender_index][3]]) + "]"    
                            words += "%s, " % words_string
                            more_sender_index += 1
                            
                        sent_timeline_data += "\t\t{value:%s, count:%s,name:[%s], words:[%s]},\n" % ( current_value, current_count, names, words)
                        sender_index = more_sender_index   
                    sent_timeline_data += "\t],\n"
                else:
                    sent_timeline_data += "\t[],\n"
                    daily_sent_timeline_data += "\t[\n"
                    for j in range(1, get_days_of_the_month(month, year) + 1):
                        daily_sent_timeline_data += "\t\t[],\n"
                    daily_sent_timeline_data += "\t],\n"
            sent_timeline_data += "]},\n"
            daily_sent_timeline_data += "]},\n"
        sent_timeline_data += "]\n"
        daily_sent_timeline_data += "]\n"
        
        logging.debug("\n\nTook : %s\n\n" % (str(time.time() - init2)))
        
        cloud_data = "["
        for token, value in key_words_manager.top_keywords:
            cloud_data += "{text: '%s', weight: %s}," % (str(token), value)
        cloud_data += "]"
        
        logging.debug("\n\nTook : %s\n\n" % (str(time.time() - init)))
        
        return self.get_from_file(INDEX_FILE_PATH) % (contacts_list_str, received_timeline_data, sent_timeline_data, contacts_to_keywords_mapping, daily_received_timeline_data, daily_sent_timeline_data, cloud_data)
        """
        
    def get_login_html(self, wrong_credentials = False, login_exception_message = None):
        if wrong_credentials:
            msg = "<span style='color:hsl(0,49%, 60%)'>Wrong username and/or password</span>"
        elif login_exception_message != None:
            msg = "<span style='color:hsl(0,49%, 60%)'>Login error: " + login_exception_message +"</span>"
        else:
            msg = ""
        return self.get_from_file(LOGIN_FILE_PATH) % (msg)
    
    def get_language_not_supported_html(self, available_boxes):
        drop_down_box = {}
        for label in ['allLabel', 'sentLabel']:
            drop_down_box[label] = "<select name='%s'>" % label
            for box in available_boxes:
                drop_down_box[label] += "<option>%s</option>" % (box)
            drop_down_box[label] += "</select>"
        return self.get_from_file(LANGUAGE_NOT_SUPPORTED_FILE_PATH) % (drop_down_box['allLabel'], drop_down_box['sentLabel'])
    
    def get_oops_html(self, msg):
        return self.get_from_file(OOPS_FILE_PATH) % repr(msg)
    
    def get_from_file(self, filename):
        """
        Prints the content of a given filename
        """
        header_filehandler = open(filename, 'r')
        return header_filehandler.read()
