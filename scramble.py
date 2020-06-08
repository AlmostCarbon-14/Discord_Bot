#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random

class Translation_Gag:
    def __init__(self, word, iterations):
        self.word = word
        self.iter = iterations
        self.chrome_options = Options()

        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--headless")
        self.langs = self.build_lang_list()
        self.opt_path = "/html/body/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/div/div[2]/div["
        self.start_lang = "English"
        self.lang_in = "English"
        self.lang_out = self.select_lang(self.langs, self.lang_in) 
    


    def build_lang_list(self):
        languages = {}
        f = open('languages.txt', 'r')
        index = 2
        for line in f:
            if line != "\n":
                languages[line[:-1]] = str(index)
                index += 1
        return languages

    def select_lang(self, langs, lang_in):
        choice = random.choice(list(self.langs.keys()))
        while choice == self.lang_in:
            choice = random.choice(list(self.langs.keys()))
        return str(choice)
        
    def select_language(self):
        self.lang_out = self.select_lang(self.langs, self.lang_in)
        menu = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
        menu.send_keys(Keys.RETURN)
        option = driver.find_element_by_xpath(opt_path + self.langs[self.lang_out] + ']')
        option.send_keys(Keys.RETURN)
        self.lang_in = self.lang_out
        return self.lang_out

    def force_language(self):
        self.lang_out = 'English'
        menu = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
        menu.send_keys(Keys.RETURN)
        option = driver.find_element_by_xpath(opt_path + self.langs[self.lang_out] + ']')
        option.send_keys(Keys.RETURN)
        self.lang_in = 'English'
        return self.lang_out

def retranslate(self):
    self.lang_out = self.start_lang
    menu = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
    menu.send_keys(Keys.RETURN)
    option = driver.find_element_by_xpath(opt_path + langs[lang_out] + ']')
    option.send_keys(Keys.RETURN)
    lang_in = lang_out
    return lang_out

def get_output(word):
    enter = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/div[1]/textarea")
    enter.clear()
    enter.send_keys(word)
    time.sleep(7)
    exit = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[1]/div[2]/div/span[1]")
    return exit.text

def main_loop(word):
    lan = select_language()
    out = get_output(word)
    print('--'  + out)
    switch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div")
    time.sleep(7)
    switch.send_keys(Keys.RETURN)
    return out

def mod_loop(word):
    lan = force_language()
    out = get_output(word)
    print('--'  + out)
    switch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div")
    time.sleep(5)
    switch.send_keys(Keys.RETURN)
    return out

def end_loop(word):
    lan = retranslate()
    out = get_output(word)
    print('[' + lan + ']' + out)

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)
driver.get("https://translate.google.com/")
time.sleep(2)
word = "When Salome Plays the Drum By James Buffet"
print("[" + start_lang + "]"  + word)
stop = 15
for x in range(0, stop):
    word = main_loop(word)
end_loop(word)
