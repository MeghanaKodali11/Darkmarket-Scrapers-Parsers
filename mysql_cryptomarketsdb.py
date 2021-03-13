# The program will scrape the ads page by page
# The URLs of ads will be written into the MariaDB database
# in the server "jaguar.cs.gsu.edu"

# Run "$ sudo apt-get install sshpass" in Ubuntu terminal if you see relevant errors.

import datetime
import os
import mysql
import mysql.connector

class MySQLcryptomarketsDB:
    # Student information
    m_sStudentNameAbbr = ""
    m_sStudentIDinDB = ""
    # The .onion link address of the Dream Market
    m_sMarketNameAbbr = ""
    m_sMarketURL = ""
    m_nMarketGlobalID = 0
    m_sMarketUserName = ""
    m_sMarketPassword = ""
    # remote SQL database server
    m_sServerHost = "jaguar.cs.gsu.edu"
    m_sServerUser = "scraper"
    m_sServerPasswd = "Im9nZe5l84RoL8r9f2no"  # Avinash updated the passwd
    m_sServerDatabaseUser = "scraper"
    m_sServerDatabasePasswd = "YW6itCLqIarX8b3c9gCr" 
    m_sServerDatabase = "cryptomarkets"
    m_sServerPort = "3306"
    m_bServerSQLBuffered = True
    # remote root directory in the file system of the server OS
    m_sRemoteRootDirectoryProductDesc = ""
    m_sRemoteRootDirectoryProductRating = ""
    m_sRemoteRootDirectoryVendorProfile = ""
    m_sRemoteRootDirectoryVendorRating = ""
    # scraping frequency for 4 kinds of web pages
    m_nScrapingFreqDaysProductDesc   = 0
    m_nScrapingFreqDaysProductRating = 0
    m_nScrapingFreqDaysVendorProfile = 0
    m_nScrapingFreqDaysVendorRating  = 0
    # vendor and product global IDs
    m_nProductGlobalID = 0
    m_nVendorGlobalID = 0
    # scraping time
    m_sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

    def MySQLQueryBasicInfor(self):
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch student information
        aSelectStmt_students_list = "SELECT student_ID FROM students_list WHERE student_name_abbr='" + self.m_sStudentNameAbbr + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt_students_list)
        if aCursorDB_cryptomarkets.rowcount == 1:
            aOneStudentRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_sStudentIDinDB = aOneStudentRecord["student_ID"]
        # Fetch market information
        aSelectStmt_cryptomarkets_list = "SELECT * FROM cryptomarkets_list WHERE cryptomarket_name_abbr='" + self.m_sMarketNameAbbr + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt_cryptomarkets_list)
        if aCursorDB_cryptomarkets.rowcount == 1:
            aOneMarketRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_sMarketURL = aOneMarketRecord["cryptomarket_url"]
            self.m_nMarketGlobalID = aOneMarketRecord["cryptomarket_global_ID"]
            self.m_sMarketUserName = aOneMarketRecord["my_username"]
            self.m_sMarketPassword = aOneMarketRecord["my_password"]
            self.m_sRemoteRootDirectoryProductDesc = aOneMarketRecord["product_desc_root_directory"]
            self.m_sRemoteRootDirectoryProductRating = aOneMarketRecord["product_rating_root_directory"]
            self.m_sRemoteRootDirectoryVendorProfile = aOneMarketRecord["vendor_profile_root_directory"]
            self.m_sRemoteRootDirectoryVendorRating = aOneMarketRecord["vendor_rating_root_directory"]
        aMariaDB_cryptomarkets.close()

    def CheckWhetherScrapingProductDescription(self, sProductMarketID):
        # Need to use (nMarketGlobalID, sProductMarketID) to determine whether we need to scrape this page (product description) or not
        # The rule is that if this page has been scraped 30 (m_nScrapingFreqDaysProductDesc) days ago, we scrape it again. Otherwise, skip.
        bWhetherScraping = True # the initial status is to scrape it
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch product information
        aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pd=1 WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pd=0;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
        nNumOfAffectedRows = aCursorDB_cryptomarkets.rowcount
        aMariaDB_cryptomarkets.commit()
        if nNumOfAffectedRows == 1: # the product is already in the product_list db, we need to check the last scraping time
            # it means 1 record is updated, we lock it.
            aSelectStmt_product_list = "SELECT product_global_ID, last_scraping_time_pd FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pd=1;"
            aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
            aOneProductRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_nProductGlobalID = aOneProductRecord["product_global_ID"]
            sLastScrapingUTCTime = aOneProductRecord["last_scraping_time_pd"] # string
            aLastScrapingUTCTime = datetime.datetime.strptime(sLastScrapingUTCTime, "%Y%m%d%H%M%S") # datetime
            aCurrentUTCTime = datetime.datetime.utcnow()
            aDuration = aCurrentUTCTime - aLastScrapingUTCTime # if the time difference is larger than 7 days
            nDurationDays = aDuration.days
            if nDurationDays < self.m_nScrapingFreqDaysProductDesc: # The condition means the last scraping date is within 30 days,
                bWhetherScraping = False #  so no need to scrape the web page again.
        else: # nNumOfAffectedRows == 0, the product is 1. not in the product_list db or 2. being checked by other program
            # check whether this product exists or not in the product_list table:
            aSelectStmt_product_list = "SELECT product_global_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND product_market_ID='" + sProductMarketID + "';"
            aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
            if aCursorDB_cryptomarkets.rowcount == 0: # this product does not exist, we need to insert this product into the table
                aInsertStmt_product_list = ("INSERT INTO product_list (cryptomarket_global_ID, product_market_ID, "
                                            "last_scraping_time_pd, my_lock_pd, last_scraping_time_pr, my_lock_pr) "
                                            "VALUES (%(cryptomarket_global_ID)s, %(product_market_ID)s, "
                                            "%(last_scraping_time_pd)s, %(my_lock_pd)s, %(last_scraping_time_pr)s, %(my_lock_pr)s)")
                aData_product_list = {
                    'cryptomarket_global_ID': self.m_nMarketGlobalID,
                    'product_market_ID': sProductMarketID,
                    'last_scraping_time_pd': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_pd': True,
                    'last_scraping_time_pr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_pr': False
                }
                aCursorDB_cryptomarkets.execute(aInsertStmt_product_list, aData_product_list)
                aMariaDB_cryptomarkets.commit()
                # need to get the product_global_ID
                aSelectStmt_product_list = "SELECT product_global_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                           + "' AND product_market_ID='" + sProductMarketID + "';"
                aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
                aOneProductRecord = aCursorDB_cryptomarkets.fetchone()
                self.m_nProductGlobalID = aOneProductRecord["product_global_ID"]
            else: # aCursorDB_cryptomarkets.rowcount == 1:
                bWhetherScraping = False # This product exists in 'product_list'; my_lock_pd = 1 : being checked by other scrapers or left as 1 by previous scrapers.
        # If the product is scraped in the last one week then we reset the lock back to 0;that means  nDurationDays < self.m_nScrapingFreqDaysProductDesc
        if bWhetherScraping == False:
            aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pd=0 WHERE cryptomarket_global_ID='" +\
                                    str(self.m_nMarketGlobalID)+ "' AND product_market_ID='" + sProductMarketID + "';"
            aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()
        return bWhetherScraping

    def UpdateDatabaseUploadFileProductDescription(self, sLocalOutputFileName, sLocalOutputFileNameFullPath, sProductMarketID):
        # Upload the local file to the sever
        sSCP_Command = 'sshpass -p \'' + self.m_sServerPasswd + '\' scp ' + sLocalOutputFileNameFullPath + ' ' + \
                       self.m_sServerUser + '@' + self.m_sServerHost + ':' + self.m_sRemoteRootDirectoryProductDesc
        os.system(sSCP_Command)
        # Insert this scraping event to the product_desc_scraping_event table in the SQL database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        aInsertStmt_product_scraping_event = (
            "INSERT INTO product_desc_scraping_event (product_global_ID, scraping_time, product_desc_file_path_in_FS, student_ID) "
            "VALUES (%(product_global_ID)s, %(scraping_time)s, %(product_desc_file_path_in_FS)s, %(student_ID)s)")
        aData_product_scraping_event = {
            'product_global_ID': self.m_nProductGlobalID,
            'scraping_time': self.m_sCurrentUTCTime,
            'product_desc_file_path_in_FS': sLocalOutputFileName,
            'student_ID': self.m_sStudentIDinDB
        }
        aCursorDB_cryptomarkets.execute(aInsertStmt_product_scraping_event, aData_product_scraping_event)
        aMariaDB_cryptomarkets.commit()
        # unlock the my_lock_pd cell of this product record in the product_list table
        aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pd=0, last_scraping_time_pd='" + self.m_sCurrentUTCTime \
                                   + "' WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pd=1;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
        aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()


    def CheckWhetherScrapingProductRating(self, sProductMarketID):
        # Need to use (nMarketGlobalID, sProductMarketID) to determine whether we need to scrape this page (product rating) or not
        # The rule is that if this page has been scraped 15 (m_nScrapingFreqDaysProductRating) days ago, we scrape it again. Otherwise, skip.
        bWhetherScraping = True # the initial status is to scrape it
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch product information
        aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pr=1 WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pr=0;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
        nNumOfAffectedRows = aCursorDB_cryptomarkets.rowcount
        aMariaDB_cryptomarkets.commit()
        if nNumOfAffectedRows == 1: # the product is already in the product_list db, we need to check the last scraping time
            # it means 1 record is updated, we lock it.
            aSelectStmt_product_list = "SELECT product_global_ID, last_scraping_time_pr FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pr=1;"
            aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
            aOneProductRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_nProductGlobalID = aOneProductRecord["product_global_ID"]
            sLastScrapingUTCTime = aOneProductRecord["last_scraping_time_pr"] # string
            aLastScrapingUTCTime = datetime.datetime.strptime(sLastScrapingUTCTime, "%Y%m%d%H%M%S") # datetime
            aCurrentUTCTime = datetime.datetime.utcnow()
            aDuration = aCurrentUTCTime - aLastScrapingUTCTime # if the time difference is larger than 7 days
            nDurationDays = aDuration.days
            if nDurationDays < self.m_nScrapingFreqDaysProductRating: # the condition means the last scraping date is within 7 days,
                bWhetherScraping = False # so no need to scrape the web page again.
        else: # nNumOfAffectedRows == 0, the product is 1. not in the product_list db or 2. being checked by other program
            # check whether this product exists or not in the product_list table:
            aSelectStmt_product_list = "SELECT product_global_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND product_market_ID='" + sProductMarketID + "';"
            aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
            if aCursorDB_cryptomarkets.rowcount == 0: # this product does not exist, we need to insert this product into the table
                aInsertStmt_product_list = ("INSERT INTO product_list (cryptomarket_global_ID, product_market_ID, "
                                            "last_scraping_time_pd, my_lock_pd, last_scraping_time_pr, my_lock_pr) "
                                            "VALUES (%(cryptomarket_global_ID)s, %(product_market_ID)s, "
                                            "%(last_scraping_time_pd)s, %(my_lock_pd)s, %(last_scraping_time_pr)s, %(my_lock_pr)s)")
                aData_product_list = {
                    'cryptomarket_global_ID': self.m_nMarketGlobalID,
                    'product_market_ID': sProductMarketID,
                    'last_scraping_time_pd': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_pd': False,
                    'last_scraping_time_pr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_pr': True
                }
                aCursorDB_cryptomarkets.execute(aInsertStmt_product_list, aData_product_list)
                aMariaDB_cryptomarkets.commit()
                # need to get the product_global_ID
                aSelectStmt_product_list = "SELECT product_global_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                           + "' AND product_market_ID='" + sProductMarketID + "';"
                aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
                aOneProductRecord = aCursorDB_cryptomarkets.fetchone()
                self.m_nProductGlobalID = aOneProductRecord["product_global_ID"]
            else: # aCursorDB_cryptomarkets.rowcount == 1:
                bWhetherScraping = False # This product exists in 'product_list'; my_lock_pr = 1 : being checked by other scrapers or left as 1 by previous scrapers.
        # If the product is scraped in the last one week then we reset the lock back to 0;that means  nDurationDays < self.m_nScrapingFreqDaysProductrating
        if bWhetherScraping == False:
            aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pr=0 WHERE cryptomarket_global_ID='" + \
                                    str(self.m_nMarketGlobalID) + "' AND product_market_ID='" + sProductMarketID + "';"
            aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()
        return bWhetherScraping

    def UpdateDatabaseUploadFileProductRating(self, sLocalOutputFileName, sLocalOutputFileNameFullPath, sProductMarketID):
        # Upload the local file to the sever
        sSCP_Command = 'sshpass -p \'' + self.m_sServerPasswd + '\' scp ' + sLocalOutputFileNameFullPath + ' ' + \
                       self.m_sServerUser + '@' + self.m_sServerHost + ':' + self.m_sRemoteRootDirectoryProductRating
        os.system(sSCP_Command)
        # Insert this scraping event to the product_rating_scraping_event table in the SQL database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        aInsertStmt_product_scraping_event = (
            "INSERT INTO product_rating_scraping_event (product_global_ID, scraping_time, product_rating_file_path_in_FS, student_ID) "
            "VALUES (%(product_global_ID)s, %(scraping_time)s, %(product_rating_file_path_in_FS)s, %(student_ID)s)")
        aData_product_scraping_event = {
            'product_global_ID': self.m_nProductGlobalID,
            'scraping_time': self.m_sCurrentUTCTime,
            'product_rating_file_path_in_FS': sLocalOutputFileName,
            'student_ID': self.m_sStudentIDinDB
        }
        aCursorDB_cryptomarkets.execute(aInsertStmt_product_scraping_event, aData_product_scraping_event)
        aMariaDB_cryptomarkets.commit()
        # unlock the my_lock_pr cell of this product record in the product_list table
        aUpdateStmt_product_list = "UPDATE product_list SET my_lock_pr=0, last_scraping_time_pr='" + self.m_sCurrentUTCTime \
                                   + "' WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND product_market_ID='" + sProductMarketID + "' AND my_lock_pr=1;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_product_list)
        aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()


    def CheckWhetherScrapingVendorProfile(self, sVendorMarketID):
        # Need to use (nMarketGlobalID, sVendorMarketID) to determine whether we need to scrape this page (vendor profile) or not
        # The rule is that if this page has been scraped 30 (m_nScrapingFreqDaysVendorProfile) days ago, we scrape it again. Otherwise, skip.
        bWhetherScraping = True # the initial status is to scrape it
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch vendor information
        aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vp=1 WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vp=0;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
        nNumOfAffectedRows = aCursorDB_cryptomarkets.rowcount
        aMariaDB_cryptomarkets.commit()
        if nNumOfAffectedRows == 1: # the vendor is already in the vendor_list db, we need to check the last scraping time
            # it means 1 record is updated, we lock it.
            aSelectStmt_vendor_list = "SELECT vendor_global_ID, last_scraping_time_vp FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vp=1;"
            aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
            aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_nVendorGlobalID = aOneVendorRecord["vendor_global_ID"]
            sLastScrapingUTCTime = aOneVendorRecord["last_scraping_time_vp"] # string
            aLastScrapingUTCTime = datetime.datetime.strptime(sLastScrapingUTCTime, "%Y%m%d%H%M%S") # datetime
            aCurrentUTCTime = datetime.datetime.utcnow()
            aDuration = aCurrentUTCTime - aLastScrapingUTCTime # if the time difference is larger than 30 days
            nDurationDays = aDuration.days
            if nDurationDays < self.m_nScrapingFreqDaysVendorProfile: # The condition means the last scraping date is within 30 days,
                bWhetherScraping = False #  so no need to scrape the web page again.
        else: # nNumOfAffectedRows == 0, the vendor is 1. not in the vendor_list db or 2. being checked by other program
            # check whether this vendor exists or not in the vendor_list table:
            aSelectStmt_vendor_list = "SELECT vendor_global_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND vendor_market_ID='" + sVendorMarketID + "';"
            aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
            if aCursorDB_cryptomarkets.rowcount == 0: # this vendor does not exist, we need to insert this vendor into the table
                aInsertStmt_vendor_list = ("INSERT INTO vendor_list (cryptomarket_global_ID, vendor_market_ID, "
                                            "last_scraping_time_vp, my_lock_vp, last_scraping_time_vr, my_lock_vr) "
                                            "VALUES (%(cryptomarket_global_ID)s, %(vendor_market_ID)s, "
                                            "%(last_scraping_time_vp)s, %(my_lock_vp)s, %(last_scraping_time_vr)s, %(my_lock_vr)s)")
                aData_vendor_list = {
                    'cryptomarket_global_ID': self.m_nMarketGlobalID,
                    'vendor_market_ID': sVendorMarketID,
                    'last_scraping_time_vp': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_vp': True,
                    'last_scraping_time_vr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_vr': False
                }
                aCursorDB_cryptomarkets.execute(aInsertStmt_vendor_list, aData_vendor_list)
                aMariaDB_cryptomarkets.commit()
                # need to get the vendor_global_ID
                aSelectStmt_vendor_list = "SELECT vendor_global_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                          + "' AND vendor_market_ID='" + sVendorMarketID + "';"
                aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
                aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
                self.m_nVendorGlobalID = aOneVendorRecord["vendor_global_ID"]
            else: # aCursorDB_cryptomarkets.rowcount == 1: it means this vendor is being updated by other program
                bWhetherScraping = False # so we do not need to update it
        # the lock is reset to 0 if vendor profile is scraped in last one week, that means  nDurationDays < self.m_nScrapingFreqDaysVendorProfile
        if bWhetherScraping == False:
            aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vp=0  WHERE cryptomarket_global_ID='" \
                                    + str(self.m_nMarketGlobalID)+ "' AND vendor_market_ID='" + sVendorMarketID + "';"
            aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()
        return bWhetherScraping

    def UpdateDatabaseUploadFileVendorProfile(self, sLocalOutputFileName, sLocalOutputFileNameFullPath, sVendorMarketID):
        # Upload the local file to the sever
        sSCP_Command = 'sshpass -p \'' + self.m_sServerPasswd + '\' scp ' + sLocalOutputFileNameFullPath + ' ' + \
                       self.m_sServerUser + '@' + self.m_sServerHost + ':' + self.m_sRemoteRootDirectoryVendorProfile
        os.system(sSCP_Command)
        # Insert this scraping event to the vendor_profile_scraping_event table in the SQL database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        aInsertStmt_vendor_scraping_event = (
            "INSERT INTO vendor_profile_scraping_event (vendor_global_ID, scraping_time, vendor_profile_file_path_in_FS, student_ID) "
            "VALUES (%(vendor_global_ID)s, %(scraping_time)s, %(vendor_profile_file_path_in_FS)s, %(student_ID)s)")
        aData_vendor_scraping_event = {
            'vendor_global_ID': self.m_nVendorGlobalID,
            'scraping_time': self.m_sCurrentUTCTime,
            'vendor_profile_file_path_in_FS': sLocalOutputFileName,
            'student_ID': self.m_sStudentIDinDB
        }
        aCursorDB_cryptomarkets.execute(aInsertStmt_vendor_scraping_event, aData_vendor_scraping_event)
        aMariaDB_cryptomarkets.commit()
        # unlock the my_lock_vp cell of this vendor record in the vendor_list table
        aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vp=0, last_scraping_time_vp='" + self.m_sCurrentUTCTime \
                                   + "' WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vp=1;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
        aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()


    def CheckWhetherScrapingVendorRating(self, sVendorMarketID):
        # Need to use (nMarketGlobalID, sVendorMarketID) to determine whether we need to scrape this page (vendor rating) or not
        # The rule is that if this page has been scraped 7 (m_nScrapingFreqDaysVendorRating) days ago, we scrape it again. Otherwise, skip.
        bWhetherScraping = True # the initial status is to scrape it
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch vendor information
        aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vr=1 WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vr=0;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
        nNumOfAffectedRows = aCursorDB_cryptomarkets.rowcount
        aMariaDB_cryptomarkets.commit()
        if nNumOfAffectedRows == 1: # the vendor is already in the vendor_list db, we need to check the last scraping time
            # it means 1 record is updated, we lock it.
            aSelectStmt_vendor_list = "SELECT vendor_global_ID, last_scraping_time_vr FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vr=1;"
            aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
            aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_nVendorGlobalID = aOneVendorRecord["vendor_global_ID"]
            sLastScrapingUTCTime = aOneVendorRecord["last_scraping_time_vr"] # string
            aLastScrapingUTCTime = datetime.datetime.strptime(sLastScrapingUTCTime, "%Y%m%d%H%M%S") # datetime
            aCurrentUTCTime = datetime.datetime.utcnow()
            aDuration = aCurrentUTCTime - aLastScrapingUTCTime # if the time difference is larger than 7 days
            nDurationDays = aDuration.days
            if nDurationDays < self.m_nScrapingFreqDaysVendorRating: # The condition means the last scraping date is within 7 days,
                bWhetherScraping = False #  so no need to scrape the web page again.
        else: # nNumOfAffectedRows == 0, the vendor is 1. not in the vendor_list db or 2. being checked by other program
            # check whether this vendor exists or not in the vendor_list table:
            aSelectStmt_vendor_list = "SELECT vendor_global_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                       + "' AND vendor_market_ID='" + sVendorMarketID + "';"
            aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
            if aCursorDB_cryptomarkets.rowcount == 0: # this vendor does not exist, we need to insert this vendor into the table
                aInsertStmt_vendor_list = ("INSERT INTO vendor_list (cryptomarket_global_ID, vendor_market_ID, "
                                            "last_scraping_time_vp, my_lock_vp, last_scraping_time_vr, my_lock_vr) "
                                            "VALUES (%(cryptomarket_global_ID)s, %(vendor_market_ID)s, "
                                            "%(last_scraping_time_vp)s, %(my_lock_vp)s, %(last_scraping_time_vr)s, %(my_lock_vr)s)")
                aData_vendor_list = {
                    'cryptomarket_global_ID': self.m_nMarketGlobalID,
                    'vendor_market_ID': sVendorMarketID,
                    'last_scraping_time_vp': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_vp': False,
                    'last_scraping_time_vr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                    'my_lock_vr': True
                }
                aCursorDB_cryptomarkets.execute(aInsertStmt_vendor_list, aData_vendor_list)
                aMariaDB_cryptomarkets.commit()
                # need to get the vendor_global_ID
                aSelectStmt_vendor_list = "SELECT vendor_global_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                          + "' AND vendor_market_ID='" + sVendorMarketID + "';"
                aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
                aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
                self.m_nVendorGlobalID = aOneVendorRecord["vendor_global_ID"]
            else: # aCursorDB_cryptomarkets.rowcount == 1:
                bWhetherScraping = False # This vendor exists in 'vendor_list'; my_lock_vr = 1 : being checked by other scrapers or left as 1 by previous scrapers.
        # the lock is reset to 0 if vendor rating is scraped in last one week, that means  nDurationDays < self.m_nScrapingFreqDaysVendorRating
        if bWhetherScraping == False:
            aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vr=0  WHERE cryptomarket_global_ID='" + str(
                self.m_nMarketGlobalID) + "' AND vendor_market_ID='" + sVendorMarketID + "';"
            aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()
        return bWhetherScraping

    def UpdateDatabaseUploadFileVendorRating(self, sLocalOutputFileName, sLocalOutputFileNameFullPath, sVendorMarketID):
        # Upload the local file to the sever
        sSCP_Command = 'sshpass -p \'' + self.m_sServerPasswd + '\' scp ' + sLocalOutputFileNameFullPath + ' ' + \
                       self.m_sServerUser + '@' + self.m_sServerHost + ':' + self.m_sRemoteRootDirectoryVendorRating
        os.system(sSCP_Command)
        # Insert this scraping event to the vendor_rating_scraping_event table in the SQL database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        aInsertStmt_vendor_scraping_event = (
            "INSERT INTO vendor_rating_scraping_event (vendor_global_ID, scraping_time, vendor_rating_file_path_in_FS, student_ID) "
            "VALUES (%(vendor_global_ID)s, %(scraping_time)s, %(vendor_rating_file_path_in_FS)s, %(student_ID)s)")
        aData_vendor_scraping_event = {
            'vendor_global_ID': self.m_nVendorGlobalID,
            'scraping_time': self.m_sCurrentUTCTime,
            'vendor_rating_file_path_in_FS': sLocalOutputFileName,
            'student_ID': self.m_sStudentIDinDB
        }
        aCursorDB_cryptomarkets.execute(aInsertStmt_vendor_scraping_event, aData_vendor_scraping_event)
        aMariaDB_cryptomarkets.commit()
        # unlock the my_lock_vr cell of this vendor record in the vendor_list table
        aUpdateStmt_vendor_list = "UPDATE vendor_list SET my_lock_vr=0, last_scraping_time_vr='" + self.m_sCurrentUTCTime \
                                   + "' WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND vendor_market_ID='" + sVendorMarketID + "' AND my_lock_vr=1;"
        aCursorDB_cryptomarkets.execute(aUpdateStmt_vendor_list)
        aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()

    def AddToProductListIfNotExist(self, sProductMarketID):
        # Use (nMarketGlobalID, sProductMarketID) to determine whether we need to add this product to table product_list or not
        # If this product does not exist, we add it. Otherwise, do not add it.
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # check whether this product exists or not in the product_list table:
        aSelectStmt_product_list = "SELECT product_global_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                   + "' AND product_market_ID='" + sProductMarketID + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
        if aCursorDB_cryptomarkets.rowcount == 0: # this product does not exist, we need to insert this product into the table
            aInsertStmt_product_list = ("INSERT INTO product_list (cryptomarket_global_ID, product_market_ID, "
                                        "last_scraping_time_pd, my_lock_pd, last_scraping_time_pr, my_lock_pr) "
                                        "VALUES (%(cryptomarket_global_ID)s, %(product_market_ID)s, "
                                        "%(last_scraping_time_pd)s, %(my_lock_pd)s, %(last_scraping_time_pr)s, %(my_lock_pr)s)")
            aData_product_list = {'cryptomarket_global_ID': self.m_nMarketGlobalID,
                                  'product_market_ID': sProductMarketID,
                                  'last_scraping_time_pd': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                                  'my_lock_pd': False,
                                  'last_scraping_time_pr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                                  'my_lock_pr': False }
            aCursorDB_cryptomarkets.execute(aInsertStmt_product_list, aData_product_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()

    def AddToVendorListIfNotExist(self, sVendorMarketID):
        # Use (nMarketGlobalID, sVendorMarketID) to determine whether we need to add this vendor to table vendor_list or not
        # If this vendor does not exist, we add it. Otherwise, do not add it.
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser, passwd=self.m_sServerDatabasePasswd,
                                        database=self.m_sServerDatabase, port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # check whether this vendor exists or not in the vendor_list table:
        aSelectStmt_vendor_list = "SELECT vendor_global_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                  + "' AND vendor_market_ID='" + sVendorMarketID + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
        if aCursorDB_cryptomarkets.rowcount == 0:  # this vendor does not exist, we need to insert this vendor into the table
            aInsertStmt_vendor_list = ("INSERT INTO vendor_list (cryptomarket_global_ID, vendor_market_ID, "
                                       "last_scraping_time_vp, my_lock_vp, last_scraping_time_vr, my_lock_vr) "
                                       "VALUES (%(cryptomarket_global_ID)s, %(vendor_market_ID)s, "
                                       "%(last_scraping_time_vp)s, %(my_lock_vp)s, %(last_scraping_time_vr)s, %(my_lock_vr)s)")
            aData_vendor_list = {'cryptomarket_global_ID': self.m_nMarketGlobalID,
                                 'vendor_market_ID': sVendorMarketID,
                                 'last_scraping_time_vp': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                                 'my_lock_vp': False,
                                 'last_scraping_time_vr': datetime.datetime.fromtimestamp(0).strftime("%Y%m%d%H%M%S"),
                                 'my_lock_vr': False }
            aCursorDB_cryptomarkets.execute(aInsertStmt_vendor_list, aData_vendor_list)
            aMariaDB_cryptomarkets.commit()
        aMariaDB_cryptomarkets.close()

    def SelectNewProductMarketIDsToBeScraped(self):
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd, database=self.m_sServerDatabase,
                                                         port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # select all new products from the product_list table:
        aLastScrapingTimeThreshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.m_nScrapingFreqDaysProductRating)
        sLastScrapingTimeThreshold = aLastScrapingTimeThreshold.strftime("%Y%m%d%H%M%S")
        aSelectStmt_product_list = "SELECT product_market_ID FROM product_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                  + "' AND last_scraping_time_pd<'" + sLastScrapingTimeThreshold + "' ORDER BY last_scraping_time_pd ASC;"
        aCursorDB_cryptomarkets.execute(aSelectStmt_product_list)
        aMariaDB_cryptomarkets.commit()
        vsAllNewProductMarketIDs = []
        for aOneProductRecord in aCursorDB_cryptomarkets.fetchall():
            sOneProductMarketID = aOneProductRecord['product_market_ID']
            vsAllNewProductMarketIDs.append(sOneProductMarketID)
        aMariaDB_cryptomarkets.close()
        return vsAllNewProductMarketIDs

    def SelectNewVendorMarketIDsToBeScraped(self):
        # query basic information of the mysql database
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost, user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd, database=self.m_sServerDatabase,
                                                         port=self.m_sServerPort, buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # select all new vendors from the vendor_list table:
        aLastScrapingTimeThreshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.m_nScrapingFreqDaysVendorRating)
        sLastScrapingTimeThreshold = aLastScrapingTimeThreshold.strftime("%Y%m%d%H%M%S")
        aSelectStmt_vendor_list = "SELECT vendor_market_ID FROM vendor_list WHERE cryptomarket_global_ID='" + str(self.m_nMarketGlobalID) \
                                  + "' AND last_scraping_time_vp<'" + sLastScrapingTimeThreshold + "' ORDER BY last_scraping_time_vp ASC;"
        aCursorDB_cryptomarkets.execute(aSelectStmt_vendor_list)
        aMariaDB_cryptomarkets.commit()
        vsAllNewVendorMarketIDs = []
        for aOneVendorRecord in aCursorDB_cryptomarkets.fetchall():
            sOneVendorMarketID = aOneVendorRecord['vendor_market_ID']
            vsAllNewVendorMarketIDs.append(sOneVendorMarketID)
        aMariaDB_cryptomarkets.close()
        return vsAllNewVendorMarketIDs
