import time
import datetime
import os
import ast

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mysql_cryptomarketsdb import MySQLcryptomarketsDB
from selenium_networksetting import *


import subprocess



process = subprocess.Popen("whoami", stdout=subprocess.PIPE)
username, error = process.communicate()

# ++++++++++++++++++++ You need to update the following 3 variables ++++++++++++++++++++
# Student Name Abbr
g_sStudentNameAbbr = "mk" # You need to update this
g_nUserName = "confused"    # You need to update this
g_nPassword = "covid123"      # You need to update this
# ++++++++++++++++++++ You need to update the above 3 variables ++++++++++++++++++++++++
# No need to change anything else below
# Scraping frequency for 4 kinds of web pages
# Number of webpages you want to scrape first. The total might be 400, but you may scrape the first 10
g_nTotalNumberOfPagesTobeVisited = 10
g_nScrapingFreqDaysProductDesc = 7 # days
g_nScrapingFreqDaysProductRating = 7 # days
g_nScrapingFreqDaysVendorProfile = 7 # days
g_nScrapingFreqDaysVendorRating = 7 # days
# market information
g_sMarketNameAbbr = "lm"
g_sMarketURL = "http://liberty4mhc252jcz6acjndbotamlajtoo43qcmz4i62lc4b2ol4aeyd.onion/signin"
g_nMarketGlobalID = 58
# local output data directory
g_sOutputDirectoryTemp = "/home/" + (username.strip()).decode('utf-8') + "/temp_scrapedhtml/"
# time to wait for human to input CAPTCHA
g_nTimeSecToWait = 30 * 24 * 60 * 60  # 30 days
# set it True if you want to use the default username and password
g_bUseDefaultUsernamePasswd = True
vendorList = []

g_vaCategoriesToScrape = []  # this list will store all the categories that will be scraped
c1  = '2'  # Fraud
c2  = '3'  # Digital products
c3  = '4'  # Counterfeit
c4  = '5'  # Services
c5  = '6'  # Software
# Only scrape categories related to financial frauds like c7,c12,c14
g_catCodes = [c4]


def Login(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    # takes you to the capture input
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'#')]")))
    aUsernameElement = aBrowserDriver.find_element_by_name("username")
    aPasswordElement = aBrowserDriver.find_element_by_name("password")
    aCaptchaElement = aBrowserDriver.find_element_by_name("challenge")
    aUsernameElement.send_keys(g_nUserName)
    aPasswordElement.send_keys(g_nPassword)
    aCaptchaElement.send_keys('')
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    sStringToBePresent = "//button[contains(@class,'btn btn-sm btn-success pt-0 pb-0')]"
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent)))
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
        else:  # sPageTitle == "Genesis Market" or the title is the title of an ad
            aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
            sStringToBePresent = "//button[contains(@class,'btn btn-sm btn-success pt-0 pb-0')]"
            aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent )))
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
    aMySQLcrptmktDB.m_nScrapingFreqDaysProductDesc = g_nScrapingFreqDaysProductDesc
    aMySQLcrptmktDB.m_nScrapingFreqDaysProductRating = g_nScrapingFreqDaysProductRating
    aMySQLcrptmktDB.m_nScrapingFreqDaysVendorProfile = g_nScrapingFreqDaysVendorProfile
    aMySQLcrptmktDB.m_nScrapingFreqDaysVendorRating = g_nScrapingFreqDaysVendorRating
    aMySQLcrptmktDB.MySQLQueryBasicInfor()
    g_nMarketGlobalID = aMySQLcrptmktDB.m_nMarketGlobalID
    if g_bUseDefaultUsernamePasswd == True:
        g_sMarketUserName = aMySQLcrptmktDB.m_sMarketUserName  # this username and passwd are retrieved from DB server
        g_sMarketPassword = aMySQLcrptmktDB.m_sMarketPassword
        g_sMarketURL = "http://liberty4mhc252jcz6acjndbotamlajtoo43qcmz4i62lc4b2ol4aeyd.onion/signin"

    # Setup Firefox browser for visiting .onion sites through Tor (AWS proxy)
    aBrowserDriver = selenium_setup_firefox_network()
    # aBrowserDriver.set_window_rect(990, 640, 465, 560) # x,y,width,height; screen width 1853, height 1145

    # Visit the BitBazaar Market sites and Login
    Login(aBrowserDriver)
    print("Login successful")

    for cat_code in g_catCodes:
        g_sMarketURL = "http://liberty4mhc252jcz6acjndbotamlajtoo43qcmz4i62lc4b2ol4aeyd.onion/category/"
        sCat_Link = g_sMarketURL + cat_code
        if cat_code == c1:
            cat_name = "Fraud"
        elif cat_code == c2:
            cat_name = "Digital Products"
        elif cat_code == c3:
            cat_name = "Counterfeits"
        elif cat_code == c4:
            cat_name = "Services"
        elif cat_code == c5:
            cat_name = "Software"
        print("Category :" + cat_name)

        NavigateToOnePage(aBrowserDriver, sCat_Link)
        # Storing all the page URLs
        numOfProductsScraped = 0
        # Get the total # of pages: "nMaxIndexOfPage"
        nIndexOfElements = 0  # the Index of the page nav element.
        nMaxIndexOfPage = 0  # The maximum number of page index, i.e., the total number of pages.
        vAllPageLinks = []
        pageList = aBrowserDriver.find_elements_by_xpath("//a[contains(@class,'btn btn-icon btn-sm border-0 btn-hover-primary mr-1 my-1 ')]")

        if len(pageList) < 2:
            nMaxIndexOfPage = 1
        else:
            nMaxIndexOfPage = len(pageList)

        nIdxOfPage = 1
        for i in range(nIdxOfPage, nMaxIndexOfPage + 1):
            sOnePageLink = sCat_Link + "?page=" + str(i)
            vAllPageLinks.append(sOnePageLink)
        print("Total number of pages %d" % nMaxIndexOfPage)

        # Start scraping. For each page, crawl all products in the page
        for sOnePageLink in vAllPageLinks:
            nPageIndex = nIdxOfPage
            nIdxOfPage += 1
            print("page %d" % nPageIndex)
            NavigateToOnePage(aBrowserDriver, sOnePageLink)
            # For each product in this page, insert them into the list of all products
            vElementsProducts = aBrowserDriver.find_elements_by_xpath(
                "//a[contains(@href,'/product/') ]")
            vAllProductsInThisPage = []
            for aElementOneProduct in vElementsProducts:
                sProductHref = aElementOneProduct.get_attribute("href")
                if sProductHref not in vAllProductsInThisPage:
                    vAllProductsInThisPage.append(sProductHref)

            # For each vendor in this page, insert them into the list of all vendors.
            vElementsVendors = aBrowserDriver.find_elements_by_xpath(
                "//a[contains(@href,'/profile/')]")
            vAllVendorsInThisPage = []
            for aElementOneVendor in vElementsVendors:
                sVendorHref = aElementOneVendor.get_attribute("href")
                if sVendorHref not in vAllVendorsInThisPage:
                    vAllVendorsInThisPage.append(sVendorHref)

            # 1. Scrape the product information
            for sProductHref in vAllProductsInThisPage:
                sProductMarketID = sProductHref.split('/')[4]
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
                    bFile = open(sLocalOutputFileNameFullPath, encoding='utf-8')
                    aBeautifulSoup = BeautifulSoup(bFile, features="html.parser")
                    productTitle = aBeautifulSoup.findChild('span', {'class': 'text-left h3'}).text[:255]

                    #print(productTitle)
                    badwords = ["sex","porn", "adult", "stolen pictures", "nudes", "pornhub","seduction",
                                "playboy", "leaked pictures", "erotic", "fucking", "whore", "penis", "ewhoring",
                                "rape", "teen", "child", "assault", "victim", "hot", "orgasm", "make love", "clitoris"]
                    badTitle = any(s in productTitle.lower() for s in badwords)
                    #if badTitle:
                        #print("Cannot insert product into DB")
                    bFile.close()
                    if not badTitle:
                        #print("Inserting product into DB")
                        numOfProductsScraped = numOfProductsScraped + 1
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileProductDescription(sLocalOutputFileName,sLocalOutputFileNameFullPath, sProductMarketID)
                    os.remove(sLocalOutputFileNameFullPath)


                ## scraping product ratings.
                bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingProductRating(sProductMarketID)
                if bWhetherScraping == True:
                    vElementsProductFeedbackHref = sProductHref + "?show=feedback"
                    NavigateToOnePage(aBrowserDriver, vElementsProductFeedbackHref)
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sProductMarketID + '_pr'
                    sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                    aFile = open(sLocalOutputFileNameFullPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()
                    bFile = open(sLocalOutputFileNameFullPath, encoding='utf-8')
                    aBeautifulSoup = BeautifulSoup(bFile, features="html.parser")
                    productTitle = aBeautifulSoup.findChild('span', {'class': 'text-left h3'}).text[:255]
                    badwords = ["sex", "porn", "adult", "stolen pictures", "nudes", "pornhub", "seduction",
                                "playboy", "leaked pictures", "erotic", "fucking", "whore", "penis", "ewhoring",
                                "rape", "teen", "child", "assault", "victim", "hot", "orgasm", "make love", "clitoris"]
                    badTitle = any(s in productTitle.lower() for s in badwords)
                    if not badTitle:
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileProductRating(sLocalOutputFileName, sLocalOutputFileNameFullPath, sProductMarketID)
                    os.remove(sLocalOutputFileNameFullPath)

            print("Products scraped till now: %d" % numOfProductsScraped)
            print("NUmber of products in this page: %d " % len(vAllProductsInThisPage))

            # 1. Scrape the vendor profile page
            for sVendorHref in vAllVendorsInThisPage:
                sVendorMarketID = sVendorHref.split('/')[4]
                NavigateToOnePage(aBrowserDriver, str(sVendorHref))
                # print(sVendorMarketID)
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

                    ## Scraping PGP key file.
                    pgpTabHref = sVendorHref + "?show=pgp"
                    NavigateToOnePage(aBrowserDriver, pgpTabHref)
                    sLocalOutputFileNamePGP = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sVendorMarketID + '_vp_pgp'
                    sLocalOutputFileNamePGPFullPath = g_sOutputDirectoryTemp + sLocalOutputFileNamePGP
                    ## saving PGP file.
                    aFile = open(sLocalOutputFileNamePGPFullPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()

                    ## Moving pgp file to jaguar and removing local files.
                    sSCP_Command = 'sshpass -p \'' + aMySQLcrptmktDB.m_sServerPasswd + '\' scp ' + sLocalOutputFileNamePGPFullPath + ' ' + \
                                   aMySQLcrptmktDB.m_sServerUser + '@' + aMySQLcrptmktDB.m_sServerHost + ':' + aMySQLcrptmktDB.m_sRemoteRootDirectoryVendorProfile
                    os.system(sSCP_Command)
                    sCommandRemoveLocalFilesPGP = 'rm ' + sLocalOutputFileNamePGPFullPath
                    os.system(sCommandRemoveLocalFilesPGP)

                    # Move file to server, and update the sql database
                    aMySQLcrptmktDB.UpdateDatabaseUploadFileVendorProfile(sLocalOutputFileName,
                                                                          sLocalOutputFileNameFullPath, sVendorMarketID)
                    sCommandRemoveLocalfiles = 'rm ' + sLocalOutputFileNameFullPath
                    os.system(sCommandRemoveLocalfiles)

                # scrape vendors feedback/rating
                bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingVendorRating(sVendorMarketID)
                if bWhetherScraping == True:
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sVendorMarketID + '_vr'
                    vElementsFeedbackHref = sVendorHref + "?show=feedback"
                    sLocalOutputFileNameFUllPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                    NavigateToOnePage(aBrowserDriver, vElementsFeedbackHref)
                    # Save the html
                    aFile = open(sLocalOutputFileNameFUllPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()
                    # Move file to server, and update the sql database
                    aMySQLcrptmktDB.UpdateDatabaseUploadFileVendorRating(sLocalOutputFileName,
                                                                         sLocalOutputFileNameFUllPath, sVendorMarketID)
                    sCommandRemoveLocalfiles = 'rm ' + sLocalOutputFileNameFUllPath
                    os.system(sCommandRemoveLocalfiles)

            print("Vendors scraped %d" % len(vAllVendorsInThisPage))

    print("All jobs are done! Thank you!")
    time.sleep(10)
    aBrowserDriver.quit()