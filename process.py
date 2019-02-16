from flask import Flask, render_template, flash, session
from lxml import html
from selenium import webdriver
import selenium
import time
import os
import numpy as np
from selenium.webdriver.chrome.options import Options

class Process(object):
    """
        This class is used to set the appropriate fields in the AVOXI test site.
        Once the fields are set, this program will wait 15 seconds so that
        the page can populate the values needed in time.

        Known issue: The country field doesn't get set properly so the user will
        have to reload the page until this can be fix.
    """
    
    def __init__(self, data):
        """
            This function loads the chromedriver to be able to interact with the website and
            sets the initial field for the user country
        """
        self.data = data
        chrome_options = Options()
        #Run browser without opening
        chrome_options.add_argument("headless")
        #Location of the chromedriver
        chromedriver = os.path.dirname(__file__) + "/chromedriver"
        self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
        self.driver.get('http://shoppingcart-staging.avoxi.io/')
        #Set the user country field on website
        self.userCountry = self.driver.find_element_by_name('userCountry')
        self.userCountry.send_keys("VoIP/SIP/Softphone")

    def processData(self, checkCountry):
        """
            This function finds the appropriate fields on the website as well as the file.
            Compares the data and adds the data to a list and returns the data back to the user
            if there are discrepancies. If no discrepancies, the file will return an exception
            or a string.
        """
        try:
            #Set the country field on website
            country = self.driver.find_element_by_name('country')
            country.send_keys(checkCountry)
            #Try to set the value again for the country field
            if country.get_attribute('value') != checkCountry:
                time.sleep(2)
                country.send_keys(checkCountry)
            elif self.userCountry.get_attribute('value') != "VoIP/SIP/Softphone":
                return("User Country does not match what the value is on the form, please reload the page or try again.")
            #Sleeping for 15 seconds so that the website can populate the values needed in time
            time.sleep(15)
            # Known issue here: The country field doesn't get set properly so the user will 
            # have to reload the page until this can be fix.
            if country.get_attribute('value') != checkCountry:
                return("Country does not match what the value is on the form, please reload the page or try again.")
            elif self.userCountry.get_attribute('value') != "VoIP/SIP/Softphone":
                return("User Country does not match what the value is on the form, please reload the page or try again.")

            #Dictionary for keys and values to look for on the website and in the file
            nameDict = dict(
                    businessClassicCard="Business Classic", 
                    businessBasicCard="Business Basic",
                    businessConnectCard="Business Connect", 
                    businessStandardCard="Business Standard", 
                    businessAdvancedCard="Business Advanced", 
                    businessPremiumCard="Business Premium"
                )

            discrepancies = list()

            # Loops through the dictionaries to find the appropriate values from the website
            # and file
            for key, value in nameDict.items():
                row = self.data.loc[(self.data['Country'] == checkCountry) & 
                (self.data['AVOXI Package Name'] == value)]

                price = self.driver.find_element_by_css_selector(
                    "div#" + key + " div#price").get_attribute('innerHTML').split('<')[0].replace('$','')

                minutesIncluded = self.driver.find_element_by_css_selector(
                    "div#" + key + " div#minutesIncluded").get_attribute('innerHTML')

                pricePerMinute = self.driver.find_element_by_css_selector(
                    "div#" + key + " div#pricePerMinute").get_attribute('innerHTML').split('<')[0].replace('$','')

                priceRow = row["MRC"].values[0]
                minutesIncludedRow = row["Minutes Incuded"].values[0]
                pricePerMinuteRow = np.round(row["Extra Minutes Price"].values[0], decimals=3)

                if str(price) != str(priceRow):
                    discrepancies.append("Discrepancy in Price for {} {}.\tWebsite: {},\tFile: {}".format(
                        checkCountry, value, price, priceRow))

                if str(minutesIncluded) != str(minutesIncludedRow):
                    discrepancies.append("Discrepancy in Minutes Included for {} {}.\tWebsite: {},\tFile: {}".format(
                        checkCountry, value, minutesIncluded, minutesIncludedRow))

                if str(pricePerMinute) != str(pricePerMinuteRow):
                    discrepancies.append("Discrepancy in Price Per Minute for {} {}.\tWebsite: {},\tFile: {}".format(
                        checkCountry, value, pricePerMinute, pricePerMinuteRow))

            if discrepancies:
                return discrepancies
            else:
                return "No Discrepancies Found"
        except selenium.common.exceptions.NoSuchElementException as e:
            # Return an exception because of the field can't be found. Usually this is because the data was 
            # searched before the website loaded completely.
            return(e)
        except Exception as e:
            # Return all other exceptions
            return(e)
