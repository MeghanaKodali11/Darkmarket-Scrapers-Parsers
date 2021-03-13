import time
import datetime
import os
import ast
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mysql_cryptomarketsdb import MySQLcryptomarketsDB
from selenium_networksetting import *

from bs4 import BeautifulSoup

import subprocess

process = subprocess.Popen("whoami", stdout=subprocess.PIPE)
username, error = process.communicate()

# ++++++++++++++++++++ You need to update the following 3 variables ++++++++++++++++++++
# Student Name Abbr
g_sStudentNameAbbr = "mk" # You need to update this
# Your Username and Password for Empire Market: http://empiremktxgjovhm.onion => sign up
g_nUserName  = "aseanking"    # You need to update this
g_nPassword  = "king234"      # You need to update this
# You must register your own account in Empire Market.
# If two students use the same username, the website will show the error message:
# "The account is logged in somewhere else"
# This error message will prevent you from scraping further. So use your own account.
# Make sure to keep anonymous when you sign up. Don't use real identity!
# ++++++++++++++++++++ You need to update the above 3 variables ++++++++++++++++++++++++
# No need to change anything else below
# Scraping frequency for 4 kinds of web pages
# Number of webpages you want to scrape first. The total might be 400, but you may scrape the first 10
g_nTotalNumberOfPagesTobeVisited = 10
g_nScrapingFreqDaysProductDesc = 3 # days
g_nScrapingFreqDaysProductRating = 3 # days
g_nScrapingFreqDaysVendorProfile = 3 # days
g_nScrapingFreqDaysVendorRating = 3 # days
# market information
g_sMarketNameAbbr = "am"
g_sMarketURL = "http://aseanm2r6znqjuackec6j7yiauyq4fcvghmskixd4xqbkvdos6eu6qyd.onion/search"
g_nMarketGlobalID = 41
# local output data directory
g_sOutputDirectoryTemp = "/home/" + (username.strip()).decode('utf-8') + "/temp_scrapedhtml/"
# time to wait for human to input CAPTCHA
g_nTimeSecToWait = 30 * 24 * 60 * 60  # 30 days
# set it True if you want to use the default username and password
g_bUseDefaultUsernamePasswd = True
vendorList = []

g_vaCategoriesToScrape = []  # this list will store all the categories that will be scraped
c1  = 'categoryId=481cf3cf-396e-4741-91b5-25fe9505c721'  # Stimulants
c2  = 'categoryId=119764f4-4490-4a2f-939a-3b9dc1b189dc'  # RC's
c3  = 'categoryId=783c4ea5-5dc0-4a82-b57c-470a402f6d82'  # Cannabis & hashish
c4  = 'categoryId=03a515e4-1026-4862-8747-56d65ec385e2'  # Drug Paraphemalia
c5  = 'categoryId=f9934eed-e35c-4201-8afc-59a4b60d09ce'  # Steroids
c6  = 'categoryId=ae728535-e367-4848-8ab1-5bca767d5202'  # Barbiturates
c7  = 'categoryId=6a99b55b-8258-4aa8-b75e-678fd4cda86d'  # Fraud
c8  = 'categoryId=cc9bfb5e-bf42-4d5f-8d73-8ffe76ac73a9'  # Weight Loss
c9  = 'categoryId=6c0a7e0f-113f-4599-9dc3-96596e190cc0'  # Ecstasy
c10 = 'categoryId=399738c9-7770-43aa-816b-ae7ad1569507'  # Prescription
c11 = 'categoryId=9988bd36-d133-467d-bffe-c8f143e17a39'  # Opiods
c12 = 'categoryId=3e709c77-3e09-46a9-9bc4-ddc7c617bfbd'  # Counterfeits
c13 = 'categoryId=de9e9133-02b4-4233-bb0c-f02851f09221'  # Dissociatives
c14 = 'categoryId=cf0b497b-bbb4-4685-85df-f15f658f0372'  # Digital Goods
c15 = 'categoryId=2704937a-22d0-4642-9e6b-f4623e6750d7'  # Benzos
c16 = 'categoryId=ae6c3317-d6ff-44a1-9b1c-ffbc16f9afa4'  # Psychedelics
# Only scrape categories related to financial frauds like c7,c12,c14
g_catCodes = [c7]


def Login(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    # takes you to the capture input
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    # what until the currecy rate of bitcoin is clickable
    aUsernameElement = aBrowserDriver.find_element_by_name("Username")
    aPasswordElement = aBrowserDriver.find_element_by_name("Password")
    aUsernameElement.send_keys(g_nUserName)
    aPasswordElement.send_keys(g_nPassword)
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    sStringToBePresent = "//a[contains(@href,'/auth/logout" + "')]"
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, sStringToBePresent)))
    time.sleep(3)


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
            aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/buyer/orders')]")))
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
        g_sMarketURL = "http://aseanm2r6znqjuackec6j7yiauyq4fcvghmskixd4xqbkvdos6eu6qyd.onion/auth/login"

    # Setup Firefox browser for visiting .onion sites through Tor (AWS proxy)
    aBrowserDriver = selenium_setup_firefox_network()
    # aBrowserDriver.set_window_rect(990, 640, 465, 560) # x,y,width,height; screen width 1853, height 1145

    # Visit the BitBazaar Market sites and Login
    Login(aBrowserDriver)
    print("Login successful")

    for cat_code in g_catCodes:
        g_sMarketURL = "http://aseanm2r6znqjuackec6j7yiauyq4fcvghmskixd4xqbkvdos6eu6qyd.onion/search?"
        sCat_Link = g_sMarketURL + cat_code
        if cat_code == c7:
            cat_name = "Fraud"
        elif cat_code == c12:
            cat_name = "Counterfiets"
        elif cat_code == c14:
            cat_name = "Digital Goods"
        print("Category :" + cat_name)

        NavigateToOnePage(aBrowserDriver, sCat_Link)
        # Storing all the page URLs

        # Get the total # of pages: "nMaxIndexOfPage"
        nIndexOfElements = 0  # the Index of the page nav element.
        nMaxIndexOfPage = 0  # The maximum number of page index, i.e., the total number of pages.
        vAllPageLinks = []
        pageList = aBrowserDriver.find_elements_by_xpath("//a[contains(@href,'/search?page=')]")

        if len(pageList) < 2:
            nMaxIndexOfPage = 1
        elif len(pageList) < 10 and len(pageList) > 1:
            LastPageLink = pageList[len(pageList) - 2]
            Last = LastPageLink.get_attribute("href")
            nMaxIndexOfPage = int(Last[82:83])
        elif len(pageList) == 10:
            LastPageLink = pageList[len(pageList) - 2]
            Last = LastPageLink.get_attribute("href")
            nMaxIndexOfPage = int(Last[82:84])
        else:
            LastPageLink = pageList[len(pageList) - 1]
            Last = LastPageLink.get_attribute("href").partition('page=')[2]
            nMaxIndexOfPage = int(Last.partition('&category')[0])

        nIdxOfPage = 1
        for i in range(nIdxOfPage, nMaxIndexOfPage + 1):
            sOnePageLink = g_sMarketURL + "page=" + str(i) + "&" + cat_code + "&sortType=None"
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
                "//a[contains(@href,'/listing') and contains(@class,'btn btn-sm btn-link btn-no-margin custom-link-action')]")
            vAllProductsInThisPage = []
            for aElementOneProduct in vElementsProducts:
                sProductHref = aElementOneProduct.get_attribute("href")
                if sProductHref not in vAllProductsInThisPage:
                    vAllProductsInThisPage.append(sProductHref)

            # For each vendor in this page, insert them into the list of all vendors.
            vElementsVendors = aBrowserDriver.find_elements_by_xpath(
                "//a[contains(@href,'/profile') and contains(@class, 'btn btn-sm btn-link btn-no-margin custom-link-action')]")
            vAllVendorsInThisPage = []
            for aElementOneVendor in vElementsVendors:
                sVendorHref = aElementOneVendor.get_attribute("href")
                if sVendorHref not in vAllVendorsInThisPage:
                    vAllVendorsInThisPage.append(sVendorHref)

            # 1. Scrape the product information
            for sProductHref in vAllProductsInThisPage:
                sProductMarketID = sProductHref.partition('listing/')[2]
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
                    aBrowserDriver.get_screenshot_as_file(sLocalOutputFileNameFullPath + "_img.png")
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
                sVendorMarketID = sVendorHref.partition('/view/')[2]
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
                    pgpTabHref = aBrowserDriver.find_element_by_xpath("//a[contains(@href,'?tab=PGP')]").get_attribute(
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
                    sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
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