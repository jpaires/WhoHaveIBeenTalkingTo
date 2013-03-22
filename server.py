# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.getcwd() + "/libs")
import cherrypy as cherrypy
import webbrowser
import urllib
import bz2

import time
from services.emailLib import GmailAccount, EmailManager, LanguageNotSupported, WrongUsernameAndOrPasswordException, SearchException, LoginException
from services.theme import Theme
from services.wordsLib import KeyWordsManager

DEFAULT_PORT = 58000

LIBS_DIR = os.path.join(os.path.abspath("."), u"libs")
THEME_CSS_DIR = os.path.join(os.path.abspath("."), u"theme/theme.css")
FAVICON_DIR = os.path.join(os.path.abspath("."), u"theme/images/favicon.ico")
LOGIN_LOCK_DIR = os.path.join(os.path.abspath("."), u"theme/images/lock.png")
LOGIN_PANEL_IMG_DIR = os.path.join(os.path.abspath("."), u"theme/images/login-panel.png")
LOGIN_WAIT_IMG_DIR = os.path.join(os.path.abspath("."), u"theme/images/login-wait.gif")

REFRESH_TIME_SECONDS = 5

DEBUG_FLAG = False

class Server(object):
    
    def __init__(self):
        self.__theme = Theme() 
        self.__key_words_manager = KeyWordsManager()
        self.__email_manager = EmailManager()
        self.__email = None
        self.__pass = None
        self.__account = None
        
        self.__index_html = None
        
        self.__error_description = ""
    
    def prepate_loop(self):
        while True:
            self.prepate()
            time.sleep(REFRESH_TIME_SECONDS)
    
    def codify(self, name):
        if not isinstance(name, str):
            return name
        new = ""
        for letter in name[:name.index("@")]:
            new += chr(int(ord(letter) + time.time()) % 122) 
        return new + name[name.index("@"):]
    
    def prepate(self):
        try:
            #f = open("debug.txt", "a")
            #f.write("----Prepare-----\n")
            emails = self.__account.get_emails()
            #f.write("emails count:%s\n" % emails.__len__())
            remaining = self.__account.emails_to_fetch_count()
            #f.write("remaining count:%s\n" % remaining)
            self.__email_manager.add_emails(emails)
            timeline = self.__email_manager.emails_timeline
            #for year in timeline:
            #    f.write("%s:\n" % year)
            #    for month in timeline[year]:
            #        f.write("\t%s:\n" % month)
            #        for type in timeline[year][month]:
            #            f.write("\t\t%s:\n" % type)
            #            for contact in timeline[year][month][type]:
            #                f.write("\t\t\t%s:%s\n" % (self.codify(contact), timeline[year][month][type][contact].__len__()))
            contacts_mapping = self.__account.get_contacts_mapping()
            #f.write("contacts mapping count:%s\n" % str(contacts_mapping.keys().__len__()))
            contacts_list = self.__account.get_contacts_list()
            #f.write("contacts list count:%s\n" % contacts_list.__len__())
            self.__index_html = self.__theme.get_index_html(remaining, self.__email_manager, timeline, contacts_mapping, contacts_list, self.__key_words_manager)
            #f.write("----------------\n\n")
            #f.close()
        except Exception as e:
            if DEBUG_FLAG:
                f = open("debug.txt", "a")
                import traceback
                traceback.print_exc(None, f)
                f.write("----------------\n\n")
                f.close()
            return
            
    @cherrypy.expose
    def index(self):
        if self.__email is None or self.__pass is None:
            return self.__theme.get_login_html()
        else:
            if self.__account == None:
                self.__account = GmailAccount(self.__key_words_manager)
                try:
                    self.__account.login(self.__email, self.__pass)
                except LanguageNotSupported as e:
                    return self.__theme.get_language_not_supported_html(e.available_boxes)
                except WrongUsernameAndOrPasswordException:
                    self.__account = None
                    return self.__theme.get_login_html(wrong_credentials = True)
                except LoginException as e:
                    self.__account = None
                    return self.__theme.get_login_html(login_exception_message = e.message)
                except SearchException as e:
                    self.__account = None
                    self.raiseOops(e)
                except Exception as e:
                    if DEBUG_FLAG:
                        f = open("debug.txt", "a")
                        import traceback
                        traceback.print_exc(None, f)
                        f.write("----------------\n\n")
                        f.close()
                    self.__account = None
                    self.raiseOops(e)
                
                try:    
                    self.__account.start_fetch_all(asynchronous=True)
                    
                    import threading
                    th = threading.Thread(target = self.prepate_loop)
                    th.start()
                except LanguageNotSupported as e:
                    return self.__theme.get_language_not_supported_html(e.available_boxes)
                except Exception as e:
                    if DEBUG_FLAG:
                        f = open("debug.txt", "a")
                        import traceback
                        traceback.print_exc(None, f)
                        f.write("----------------\n\n")
                        f.close()
                    self.raiseOops(e)
            
            if self.__index_html is None or self.__index_html.__len__() == 0:
                time.sleep(1)
                raise cherrypy.HTTPRedirect('./index')
            else:
                try:
                    return self.__index_html
                except Exception as e:
                    if DEBUG_FLAG:
                        f = open("debug.txt", "a")
                        import traceback
                        traceback.print_exc(None, f)
                        f.write("----------------\n\n")
                        f.close()
                    self.raiseOops(e)
    
    @cherrypy.expose
    def choose_label_action(self, allLabel, sentLabel):
        try:
            self.__account.SUPORTED_ALL_MAIL_LABELS.append(allLabel)
            self.__account.SUPORTED_SENT_MAIL_LABELS.append(sentLabel)
            self.__account = None
        except Exception as e:
            self.raiseOops(e)
            
        raise cherrypy.HTTPRedirect('./index')
    
    @cherrypy.expose
    def login_action(self, mail, password):
        try:
            self.__email = mail
            self.__pass = password
        except Exception as e:
            if DEBUG_FLAG:
                f = open("debug.txt", "a")
                import traceback
                traceback.print_exc(None, f)
                f.write("----------------\n\n")
                f.close()
            self.raiseOops(e)
        raise cherrypy.HTTPRedirect('./index')
    
    @cherrypy.expose
    def logout_action(self):
        try:
            self.__email = None
            self.__pass = None
        except Exception as e:
            self.raiseOops(e)
        raise cherrypy.HTTPRedirect('./index')
    
    
    def raiseOops(self, exception):
        msg = str(exception)
        if msg.__len__() == 0:
            msg = "no description"
        encrypte_msg = bz2.compress(msg)
        self.__error_description = encrypte_msg
        raise cherrypy.HTTPRedirect('./oops')
    
    @cherrypy.expose
    def oops(self):
        return self.__theme.get_oops_html(self.__error_description)


config = {'/libs':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': LIBS_DIR,
                },
          '/favicon.ico':
                {
                 'tools.staticfile.on' : True,
                 'tools.staticfile.filename' : FAVICON_DIR,
                },
            '/theme.css':
                {
                 'tools.staticfile.on' : True,
                 'tools.staticfile.filename' : THEME_CSS_DIR,
                },
            '/login-panel.png':
                {
                 'tools.staticfile.on' : True,
                 'tools.staticfile.filename' : LOGIN_PANEL_IMG_DIR,
                }, 
            '/lock.png':
                {
                 'tools.staticfile.on' : True,
                 'tools.staticfile.filename' : LOGIN_LOCK_DIR,
                }, 
            '/login-wait.gif':
                {
                 'tools.staticfile.on' : True,
                 'tools.staticfile.filename' : LOGIN_WAIT_IMG_DIR,
                },
        }

def open_page():
    webbrowser.open("http://127.0.0.1:%i/" % (DEFAULT_PORT))

cherrypy.config.update({'server.socket_host': '127.0.0.1',
                        'server.socket_port': DEFAULT_PORT,
                       })

cherrypy.config["tools.encode.on"] = False
cherrypy.config["tools.encode.encoding"] = "utf-8"

cherrypy.config["tools.response_headers.on"] = True


cherrypy.config["tools.gzip.on"] = True
cherrypy.config["tools.gzip.mime_types"] = ['application/xml']

cherrypy.config["tools.encode.text_only"] = False

cherrypy.response.headers['Content-Type']='text/xml; charset=utf-8'
cherrypy.response.headers['Content-Disposition']='downloaded-article.xml'
cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(Server(), '/', config = config)
cherrypy.engine.start()
