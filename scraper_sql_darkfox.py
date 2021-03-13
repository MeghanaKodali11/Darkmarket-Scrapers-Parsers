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
g_nTotalNumberOfPagesTobeVisited = 2
# Scraping frequency for 4 kinds of web pages
g_nScrapingFreqDaysProductDesc = 3 # days
g_nScrapingFreqDaysProductRating = 3 # days
g_nScrapingFreqDaysVendorProfile = 3 # days
g_nScrapingFreqDaysVendorRating = 3 # days
# market information
g_sMarketNameAbbr = "df"
g_sMarketURL = "http://57d5j6hfzfpsfev6c7f5ltney5xahudevvttfmw4lrtkt42iqdrkxmqd.onion/"
g_nMarketGlobalID = 44
# local output data directory
g_sOutputDirectoryTemp = "/home/" + (username.strip()).decode('utf-8') + "/temp_scrapedhtml/"
# time to wait for human to input CAPTCHA
g_nTimeSecToWait = 30 * 24 * 60 * 60  # 30 days
# set it True if you want to use the default username and password
g_bUseDefaultUsernamePasswd = True
g_nUserName = "foxes123"
g_nPassword = "foxgroup" # pin1234
#frighten creator pig music flirt add cookie march shown possible direction yours peaceful bar such mom hunt bring support screen grand wonderful valley bother
vendorList = []



g_vaCategoriesToScrape = [] # this list will store all the categories that will be scraped
#c1 ='/14d45d7f-1e6f-4b60-b324-1ef9a7cffeaa' #Dumps
#c1 ='/7500f3b2-c29c-430e-8d26-3cb59282f80c' #Personal Info
#c1 ='/9a5aa3b3-bcad-4819-b0e5-d1d35eb1f221' #Accounts & Drops
c1 = '/ed129c6a-90a8-4a54-a227-0ab8c2abb968' #Cards and CVV
#c1 = '/5dd24d32-25a5-4605-8001-04ab79db3982' #Data & Scans
c2 ='/1f361bde-fbdb-42dd-92bf-fc30891408c6' #Counterfeits
#Scrape Fraud and Counterfiet listings
g_catCodes = [c1]



def Login(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    # takes you to the capture input
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    sStringToBePresent = "//a[contains(@href,'/password/reset')]"
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent)))
    # what until the currency rate of bitcoin is clickable
    aUsernameElement = aBrowserDriver.find_element_by_name("username")
    aPasswordElement = aBrowserDriver.find_element_by_name("password")
    aCaptchaElement = aBrowserDriver.find_element_by_name("captcha")
    aUsernameElement.send_keys(g_nUserName)
    aPasswordElement.send_keys(g_nPassword)
    aCaptchaElement.send_keys("")
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    sStringToBePresent = "//a[contains(@href,'/signout" + "')]"
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent)))
    time.sleep(2)



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
            aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//i[contains(@class,'fi fi-bitcoin-circle m-r-xs')]")))
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
        g_sMarketURL = "http://57d5j6hfzfpsfev6c7f5ltney5xahudevvttfmw4lrtkt42iqdrkxmqd.onion/signin"

    # Setup Firefox browser for visiting .onion sites through Tor (AWS proxy)
    aBrowserDriver = selenium_setup_firefox_network()
    # aBrowserDriver.set_window_rect(990, 640, 465, 560) # x,y,width,height; screen width 1853, height 1145

    # Visit the BitBazaar Market sites and Login
    Login(aBrowserDriver)
    print("Login successful")

    for cat_code in g_catCodes:
        g_sMarketURL = "http://57d5j6hfzfpsfev6c7f5ltney5xahudevvttfmw4lrtkt42iqdrkxmqd.onion/category"
        sCat_Link = g_sMarketURL + cat_code
        if cat_code == c1:
            cat_name = "Fraud"
        elif cat_code == c2:
            cat_name = "Counterfiets"
        print("Category :" + cat_name)
        NavigateToOnePage(aBrowserDriver, sCat_Link)
        # Get the total # of pages: "nMaxIndexOfPage"
        nIndexOfElements = 0  # the Index of the page nav element.
        nMaxIndexOfPage = 0  # The maximum number of page index, i.e., the total number of pages.
        vAllPageLinks = []
        pageList = aBrowserDriver.find_elements_by_xpath("//a[contains(@class,'pagination-link')]")
        len(pageList)
        if len(pageList) < 2:
            nMaxIndexOfPage = 1
        else:
            LastPageLink = pageList[len(pageList) - 1]
            Last = LastPageLink.get_attribute("href")
            nMaxIndexOfPage = int(Last.partition('?page=')[2])
        nIdxOfPage = 7
        for i in range(nIdxOfPage, nMaxIndexOfPage + 1):
            sOnePageLink = g_sMarketURL + cat_code + "?page=" + str(i)
            vAllPageLinks.append(sOnePageLink)
        print("Total number of pages %d" % nMaxIndexOfPage)

        # Start scraping. For each page, crawl all products in the page
        for sOnePageLink in vAllPageLinks:
            nPageIndex = nIdxOfPage
            nIdxOfPage += 1
            print("page %d" % nPageIndex)
            NavigateToOnePage(aBrowserDriver, sOnePageLink)

            # For each product in this page, insert them into the list of all products
            vElementsProducts = aBrowserDriver.find_elements_by_xpath("//a[contains(@class,'button is-expanded is-link is-rounded is-fullwidth') ]")
            vAllProductsInThisPage = []
            for aElementOneProduct in vElementsProducts:
                sProductHref = aElementOneProduct.get_attribute("href")
                if sProductHref not in vAllProductsInThisPage:
                    vAllProductsInThisPage.append(sProductHref)


            # For each vendor in this page, insert them into the list of all vendors.
            vElementsVendors = aBrowserDriver.find_elements_by_xpath(
                "//a[contains(@href,'/user')]")
            vAllVendorsInThisPage = []
            for aElementOneVendor in vElementsVendors:
                sVendorHref = aElementOneVendor.get_attribute("href")
                if sVendorHref not in vAllVendorsInThisPage:
                    vAllVendorsInThisPage.append(sVendorHref)

            # 1. Scrape the product information
            for sProductHref in vAllProductsInThisPage:
                sProductMarketID = sProductHref.partition('product/')[2]
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

                ## scraping product ratings.
                bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingProductRating(sProductMarketID)
                if bWhetherScraping == True:
                    vElementsProductFeedbackHref = sProductHref + "/feedback"
                    NavigateToOnePage(aBrowserDriver, vElementsProductFeedbackHref)
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sProductMarketID + '_pr'
                    sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                    aFile = open(sLocalOutputFileNameFullPath, "w")
                    aFile.write(aBrowserDriver.page_source)
                    aFile.close()
                    aMySQLcrptmktDB.UpdateDatabaseUploadFileProductRating(sLocalOutputFileName,
                                                                          sLocalOutputFileNameFullPath,
                                                                          sProductMarketID)
                    os.remove(sLocalOutputFileNameFullPath)

            print("Products scraped : %d" % len(vAllProductsInThisPage))

            # 1. Scrape the vendor profile page
            for sVendorHref in vAllVendorsInThisPage:
                sVendorMarketID = sVendorHref.partition('/user/')[2]
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
                    pgpTabHref = aBrowserDriver.find_element_by_xpath("//a[contains(@href,'pgp') and contains(@href,'user')]").get_attribute(
                        "href")
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
                    sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(
                        2) + '_' + sVendorMarketID + '_vr'
                    vElementsFeedbackHref = sVendorHref + "/feedback"
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