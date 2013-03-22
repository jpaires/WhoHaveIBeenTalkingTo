# -*- coding: utf-8 -*-
'''
Created on 18 de Abr de 2011

@author: joao
'''
import logging
import math
from services.tokenizer import Tokenize
from services.emailLib import RECEIVED_TYPE_ID, SENT_TYPE_ID, get_contact_address

MAX_TOP_KEYWORDS = 50
DEBUG = True

class KeyWordsManager:
    
    def __init__(self):
        self.__is_dirty = False
        
        self.__term_count = {}
        self.__total_terms_count = 0
        self.__term_document_count = {}
        self.__document_count = 0
        
        self.__contact_term_count = {}
        self.__contact_total_terms_count = {}
        self.__contact_term_document_count = {}
        self.__contact_document_count = {}
        
        self.__keywords_importance = {}
        self.__contact_keywords_importance = {}
            
    def get_key_words(self, contact = None):
        if contact == None:
            return self.__term_count
    
    def get_top_key_words(self):
        if self.__is_dirty:
            self.__compute_keywords()
        
        return [[token, self.__keywords_importance[token]] for token in (sorted(self.__keywords_importance, key=self.__keywords_importance.__getitem__, reverse=True)[:MAX_TOP_KEYWORDS])]
    
    def get_contact_top_keywords(self, contact):
        if self.__is_dirty:
            self.__compute_keywords()
        
        contact = get_contact_address(contact)
        try:
            return [[token, self.__contact_keywords_importance[contact][token]] for token in (sorted(self.__contact_keywords_importance[contact], key=self.__contact_keywords_importance[contact].__getitem__, reverse=True)[:MAX_TOP_KEYWORDS])]
        except Exception as e:
            return []
    
    
    top_keywords = property(get_top_key_words, None)
    
    def process_email(self, email):
        
        contacts = []
        if email.type == RECEIVED_TYPE_ID:
            contacts = [email.sender_address]
        else:
            contacts = email.recipient_address
        
        for contact in contacts:
            if not( contact in self.__contact_document_count):
                self.__contact_document_count[contact] = 0
            self.__contact_document_count[contact] += 1
        
        self.__document_count += 1
        
        self.process_tokens(email)
    
    def __term_frequency(self, times_term, total_terms_count):
        if DEBUG:
            if times_term > total_terms_count:
                logging.debug("\n\nWarning: '_term_frequency'@'wordsLib' times_term (%s) should be <= total_terms_count (%s)\n\n" % (times_term, total_terms_count))
        return float(times_term)/float(total_terms_count)
    
    def __inverse_document_frequency(self, documents_containing_term, total_documents_count):
        if DEBUG:
            if documents_containing_term > total_documents_count:
                logging.debug("\nWARNING documents_containing_term (%s) should be <= total_documents_count (%s)" % (documents_containing_term, total_documents_count))
        return math.log10(float(total_documents_count)/float(documents_containing_term)) 
    
    def __tf_idf(self, times_term, total_terms_count, documents_containing_term, total_documents_count):
        return self.__term_frequency(times_term, total_terms_count) * self.__inverse_document_frequency(documents_containing_term, total_documents_count)
    
    def __add_token_occurrences(self, token, count, contact = None):
        if contact is None:
            term_count_struct = self.__term_count
            term_document_count_struct = self.__term_document_count
        else:
            try:
                term_count_struct = self.__contact_term_count[contact]
            except KeyError:
                self.__contact_term_count[contact] = {}
                term_count_struct = self.__contact_term_count[contact]
                
            try:
                term_document_count_struct = self.__contact_term_document_count[contact]
            except KeyError:
                self.__contact_term_document_count[contact] = {}
                term_document_count_struct = self.__contact_term_document_count[contact]
        
        if token in term_count_struct:
            term_count_struct[token]+=count
            term_document_count_struct[token] += 1
        else:
            term_count_struct[token] = count
            term_document_count_struct[token] = 1
            
        if contact is None:
            self.__total_terms_count += count
        else:
            try:
                self.__contact_total_terms_count[contact] += count
            except KeyError:
                self.__contact_total_terms_count[contact] = count
        
        self.__is_dirty = True
    
    def __compute_term_importance(self, token, contact = None):
        if contact is None:
            term_count = self.__term_count[token]
            total_term_count = self.__total_terms_count
            document_with_term_count = self.__term_document_count[token]
            total_document_count = self.__document_count
        else:
            term_count = self.__contact_term_count[contact][token]
            total_term_count = self.__contact_total_terms_count[contact]
            document_with_term_count = self.__contact_term_document_count[contact][token]
            total_document_count = self.__contact_document_count[contact]
        
        try:
            token_importance = self.__tf_idf(term_count, total_term_count, document_with_term_count, total_document_count)
        except Exception as e:
            logging.debug("\nErro tf-idf " + str(e) + " \n tfidf(%s, %s, %s, %s)" % (term_count, total_term_count, document_with_term_count, total_document_count))
        
        return token_importance
    
    def __add_token_importance(self, token, token_importance, contact = None):
        if contact is None:
            self.__keywords_importance[token] = token_importance
        else:
            try:
                contact_keywords = self.__contact_keywords_importance[contact]
            except KeyError:
                self.__contact_keywords_importance[contact] = {}
                contact_keywords = self.__contact_keywords_importance[contact]
            
            contact_keywords[token] = token_importance
    
    def __compute_keywords(self):
        for token in self.__term_count:
            token_importance = self.__compute_term_importance(token)
            self.__add_token_importance(token, token_importance)
        for contact in self.__contact_term_count:
            for token in self.__contact_term_count[contact]:
                token_importance = self.__compute_term_importance(token, contact)
                self.__add_token_importance(token, token_importance, contact)
        
        self.__is_dirty = False
    
    def process_tokens(self, email):
        email.tokenized_words = {}
        tokens = Tokenize(email.subject)
        for token in tokens:
            if token in email.tokenized_words:
                email.tokenized_words[token]+=1
            else:
                email.tokenized_words[token] = 1 
            
        for token in email.tokenized_words:
            count = email.tokenized_words[token]
            self.__add_token_occurrences(token, count)
            if email.type == SENT_TYPE_ID:
                contacts = email.recipient_address
            else:
                contacts = [email.sender_address]
                
            for contact in contacts:
                self.__add_token_occurrences(token, count, contact)