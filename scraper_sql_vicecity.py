import time
import datetime
import os
import ast
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mysql_cryptomarketsdb import MySQLcryptomarketsDB
from selenium_networksetting import *

import subprocess


process = subprocess.Popen("whoami", stdout=subprocess.PIPE)
username, error = process.communicate()

g_sStudentNameAbbr = "mk"

# Number of webpages you want to scrape first. The total might be 400, but you may scrape the first 10
g_nTotalNumberOfPagesTobeVisited = 10
# Scraping frequency for 4 kinds of web pages
g_nScrapingFreqDaysProductDesc = 3 # days
g_nScrapingFreqDaysProductRating = 10 # days
g_nScrapingFreqDaysVendorProfile = 3 # days
g_nScrapingFreqDaysVendorRating = 10 # days
# market information
g_sMarketNameAbbr = "vc"
g_sMarketURL = " http://vice2e3gr3pmaikukidllstulxvkb7a247gkguihzvyk3gqwdpolqead.onion/"
g_nMarketGlobalID = 48
# local output data directory
g_sOutputDirectoryTemp = "/home/" + (username.strip()).decode('utf-8') + "/temp_scrapedhtml/"
# time to wait for human to input CAPTCHA
g_nTimeSecToWait = 30 * 24 * 60 * 60  # 30 days
# set it True if you want to use the default username and password
g_bUseDefaultUsernamePasswd = True
g_nUserName = "viceking"
g_nPassword = "king123" # pin1234
vendorList = []

g_vaCategoriesToScrape = [] # this list will store all the categories that will be scraped
c1='85' #Benzos
c2='84' #Cannabis
c3='97' #Dissociatives
c4='86' #Ecstacy
c5='87' #Opiods
c6='92' #Other Drugs
c7='88' #Presciptions
c8='91' #Psychedelics
c9='89' #Steroids
c10='90' #Stimulants
c11='93' #digital
c12='72' #Fraud
c13='96' #Other Listings
c14='95' #Services
#Scrape Fraud and Counterfiet listings
g_catCodes = [c11]



def Login(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    # takes you to the capture input
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'rg2')]")))
    aUsernameElement = aBrowserDriver.find_element_by_name("username")
    aCaptchaElement = aBrowserDriver.find_element_by_name("code")
    aUsernameElement.send_keys(g_nUserName)
    aCaptchaElement.send_keys('')
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    sStringToBePresent = "//input[contains(@name,'submitAuth')]"
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent)))
    time.sleep(3)

def Password(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'login.php?cancelLogin')]")))
    aPasswordElement = aBrowserDriver.find_element_by_name("password")
    aPasswordElement.send_keys(g_nPassword)
    submit_button = aBrowserDriver.find_elements_by_xpath("//input[contains(@name,'submitAuth')]")[0]
    submit_button.click()
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'orders')]")))
    time.sleep(1)



def NavigateToOnePage(aBrowserDriver, sPageLink):
    # "aBrowserDriver" : web driver
    # "sPageLink" : the link of the web page
    while True:
        aBrowserDriver.get(sPageLink)
        # Get the page title
        sPageTitle = aBrowserDriver.title
        if '(Privoxy@localhost)' in sPageTitle:
            # 502 - No server or forwarder data received (Privoxy@localhost)
            # 503 - Forwarding failure (Privoxy@localhost)
            # 504 - Connection timeout (Privoxy@localhost)
            aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
            aWaitNextPage.until(EC.element_to_be_clickable((By.LINK_TEXT, "Privoxy")))
        else:
            aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
            aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'?page=orders')]")))
            break
        # Sleep for a while and then go to next page
        time.sleep(1)
    # Wait for 1 second before scraping next page.
    time.sleep(1)

# The main function, the entry point
if __name__ == '__main__':

    # query the SQL server to retrieve some basic information
    aMySQLcrptmktDB = MySQLcryptomarketsDB()
    aMySQLcrptmktDB.m_sStudentNameAbbr = g_sStudentNameAbbr
    aMySQLcrptmktDB.m_sMarketNameAbbr = g_sMarketNameAbbr
    aMySQLcrptmktDB.m_nScrapingFreqDaysProductDesc   = g_nScrapingFreqDaysProductDesc
    aMySQLcrptmktDB.m_nScrapingFreqDaysProductRating = g_nScrapingFreqDaysProductRating
    aMySQLcrptmktDB.m_nScrapingFreqDaysVendorProfile = g_nScrapingFreqDaysVendorProfile
    aMySQLcrptmktDB.m_nScrapingFreqDaysVendorRating  = g_nScrapingFreqDaysVendorRating
    aMySQLcrptmktDB.MySQLQueryBasicInfor()
    g_nMarketGlobalID = aMySQLcrptmktDB.m_nMarketGlobalID
    if g_bUseDefaultUsernamePasswd == True:
        g_sMarketUserName = aMySQLcrptmktDB.m_sMarketUserName # this username and passwd are retrieved from DB server
        g_sMarketPassword = aMySQLcrptmktDB.m_sMarketPassword
        g_sMarketURL = "http://vice2e3gr3pmaikukidllstulxvkb7a247gkguihzvyk3gqwdpolqead.onion/login.php"

    # Setup Firefox browser for visiting .onion sites through Tor (AWS proxy)
    aBrowserDriver = selenium_setup_firefox_network()
    # aBrowserDriver.set_window_rect(990, 640, 465, 560) # x,y,width,height; screen width 1853, height 1145

    # Visit the BitBazaar Market sites and Login
    Login(aBrowserDriver)
    Password(aBrowserDriver)
    print("Login successful")

    for cat_code in g_catCodes:
        g_sMarketURL = " http://vice2e3gr3pmaikukidllstulxvkb7a247gkguihzvyk3gqwdpolqead.onion/?category="
        sCat_Link = g_sMarketURL + cat_code
        if cat_code == c11:
            cat_name = "Digital"
        elif cat_code == c12:
            cat_name = "Fruad"
        elif cat_code == c13:
            cat_name = "Other Listings"
        elif cat_code == c14:
            cat_name = "Services"
        print("Category :" + cat_name)
        NavigateToOnePage(aBrowserDriver, sCat_Link)
        # Get the total # of pages: "nMaxIndexOfPage"
        nIndexOfElements = 0  # the Index of the page nav element.
        nMaxIndexOfPage = 0  # The maximum number of page index, i.e., the total number of pages.
        vAllPageLinks = []
        pageList = aBrowserDriver.find_elements_by_xpath("//a[contains(@class,'pagination_link')]")
        len(pageList)
        if len(pageList) < 2:
            nMaxIndexOfPage = 1
        else:
            LastPageLink = pageList[len(pageList) - 1]
            Last = LastPageLink.get_attribute("href")
            nMaxIndexOfPage = int(Last.partition('&pg=')[2])
        nIdxOfPage = 12
        for i in range(nIdxOfPage, nMaxIndexOfPage + 1):
            sOnePageLink = g_sMarketURL + cat_code + "&pg=" + str(i)
            vAllPageLinks.append(sOnePageLink)
        print("Total number of pages %d" % nMaxIndexOfPage)

        # Start scraping. For each page, crawl all products in the page
        for sOnePageLink in vAllPageLinks:
            nPageIndex = nIdxOfPage
            nIdxOfPage += 1
            print("page %d" % nPageIndex)
            NavigateToOnePage(aBrowserDriver, sOnePageLink)

            # For each product in this page, insert them into the list of all products
            vElementsProducts = aBrowserDriver.find_elements_by_xpath("//div[contains(@class,'wLfName')]/a")
            vAllProductsInThisPage = []
            for aElementOneProduct in vElementsProducts:
                sProductHref = aElementOneProduct.get_attribute("href")
                if sProductHref not in vAllProductsInThisPage:
                    vAllProductsInThisPage.append(sProductHref)


            # For each vendor in this page, insert them into the list of all vendors.
            vElementsVendors = aBrowserDriver.find_elements_by_xpath("//a[contains(@href,'?page=profile&user=')]")
            vAllVendorsInThisPage = []
            for aElementOneVendor in vElementsVendors:
                sVendorHref = aElementOneVendor.get_attribute("href")
                if sVendorHref not in vAllVendorsInThisPage:
                    vAllVendorsInThisPage.append(sVendorHref)

            # 1. Scrape the product information
            for sProductHref in vAllProductsInThisPage:
                sProductMarketID = sProductHref.partition('lid=')[2]
                bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingProductDescription(sProductMarketID)
                if bWhetherScraping == True:
                    NavigateToOnePage(aBrowserDriver, sProductHref)
                    # Save the html
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sProductMarketID + '_pd'
                    sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                    # Get screen shot of Product Description
                    #aBrowserDriver.get_screenshot_as_file(sLocalOutputFileNameFullPath + "_img.png")
                    aFile = open(sLocalOutputFileNameFullPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()

                    aMySQLcrptmktDB.UpdateDatabaseUploadFileProductDescription(sLocalOutputFileName,
                                                                               sLocalOutputFileNameFullPath,
                                                                               sProductMarketID)
                    os.remove(sLocalOutputFileNameFullPath)

                ## product ratings are in same page of product descriptions

            print("Products scraped : %d" % len(vAllProductsInThisPage))

            # 1. Scrape the vendor profile page
            for sVendorHref in vAllVendorsInThisPage:
                sVendorMarketID = sVendorHref.partition('&user=')[2]
                NavigateToOnePage(aBrowserDriver, str(sVendorHref))
                bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingVendorProfile(sVendorMarketID)
                if bWhetherScraping == True:
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sVendorMarketID + '_vp'
                    sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                    # Save the html
                    aFile = open(sLocalOutputFileNameFullPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()
                    aMySQLcrptmktDB.UpdateDatabaseUploadFileVendorProfile(sLocalOutputFileName,
                                                                               sLocalOutputFileNameFullPath,
                                                                               sVendorMarketID)
                    os.remove(sLocalOutputFileNameFullPath)

                # vendors feedback/rating and pgp are in the same html page

            print("Vendors scraped %d" % len(vAllVendorsInThisPage))

    print("All jobs are done! Thank you!")
    time.sleep(10)
    aBrowserDriver.quit()
