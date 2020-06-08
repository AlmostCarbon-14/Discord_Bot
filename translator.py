
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random

class Translation_Gag:
    
    def __init__(self, word, iterations):
        self.word = word
        self.iter = int(iterations)
        self.chrome_options = Options()

        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--headless")
        self.langs = self.build_lang_list()
        self.opt_path = "/html/body/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/div/div[2]/div["
        self.start_lang = "English"
        self.lang_in = "English"
        self.lang_out = self.select_lang(self.langs, self.lang_in) 
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options = self.chrome_options)
        self.driver.get("https://translate.google.com/")
        time.sleep(2)
        print("[" + self.start_lang + "]"  + self.word)
        for x in range(0, self.iter):
            self.word = self.main_loop(self.word)
        self.end_loop(self.word)  


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
        menu = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
        menu.send_keys(Keys.RETURN)
        option = self.driver.find_element_by_xpath(self.opt_path + self.langs[self.lang_out] + ']')
        option.send_keys(Keys.RETURN)
        self.lang_in = self.lang_out
        return self.lang_out

    def force_language(self):
        self.lang_out = 'English'
        menu = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
        menu.send_keys(Keys.RETURN)
        option = self.driver.find_element_by_xpath(self.opt_path + self.langs[self.lang_out] + ']')
        option.send_keys(Keys.RETURN)
        self.lang_in = 'English'
        return self.lang_out

    def retranslate(self):
        self.lang_out = self.start_lang
        menu = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[4]/div[3]")
        menu.send_keys(Keys.RETURN)
        option = self.driver.find_element_by_xpath(self.opt_path + self.langs[self.lang_out] + ']')
        option.send_keys(Keys.RETURN)
        self.lang_in = self.lang_out
        return self.lang_out

    def get_output(self, word):
        enter = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/div[1]/textarea")
        enter.clear()
        enter.send_keys(word)
        time.sleep(7)
        exit = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[1]/div[2]/div/span[1]")
        return exit.text

    def main_loop(self, word):
        lan = self.select_language()
        out = self.get_output(word)
        print('-->'  + out)
        switch = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div")
        time.sleep(7)
        switch.send_keys(Keys.RETURN)
        return out

    def mod_loop(self, word):
        lan = self.force_language()
        out = self.get_output(word)
        print('-->'  + out)
        switch = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div")
        time.sleep(5)
        switch.send_keys(Keys.RETURN)
        return out

    def end_loop(self, word):
        lan = self.retranslate()
        out = self.get_output(word)
        print('[' + lan + ']' + out)

