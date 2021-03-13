import datetime
import os
import mysql
import mysql.connector


class parser_base:
    # This is the base class for all other parsers for cryptomarkets
    # First, define and initialize all member variables
    def __init__(self):
        # member variables for table 'parser_progress'
        self.m_n_last_parsed_scraping_event_ID_pd = 0
        self.m_n_last_parsed_scraping_event_ID_pd_4pr = 0
        self.m_n_last_parsed_scraping_event_ID_pr = 0
        self.m_n_last_parsed_scraping_event_ID_vp = 0
        self.m_n_last_parsed_scraping_event_ID_vp_4vr = 0
        self.m_n_last_parsed_scraping_event_ID_vr = 0
        # member variables for table 'product_ratings' and 'vendor_ratings'
        self.m_s_buyer_market_ID = ''  # other variables exists below
        self.m_f_rating_stars = -1
        self.m_s_text_comments = ''
        self.m_s_post_date = ''
        self.m_f_money_bitcoin = -1
        self.m_f_money_monero = -1
        self.m_f_money_usd = -1
        self.m_f_money_eur = -1
        self.m_n_buyer_total_num_of_orders = -1
        self.m_f_buyer_total_value_of_orders = -1
        self.m_s_product_market_ID = ''
        # member variables for table 'product_descriptions'
        self.m_s_scraping_time = ''
        self.m_n_cryptomarket_global_ID = 0
        self.m_n_product_global_ID = 0
        self.m_n_vendor_global_ID = 0
        self.m_s_vendor_market_ID = ''
        self.m_s_vendor_market_name = ''
        self.m_s_product_title = ''
        self.m_s_product_desc = ''
        self.m_f_price_usd = -1
        self.m_f_price_eur = -1
        self.m_f_price_bitcoin = -1
        self.m_s_ships_to = ''
        self.m_s_ships_from = ''
        self.m_s_escrow = ''
        self.m_s_category = ''
        self.m_n_num_sales = -1
        self.m_n_num_stock = -1
        self.m_s_quantity_in_stock = ''
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_s_already_sold = ''
        self.m_n_num_views = 0
        self.m_s_ads_post_date = ''  # ads_post_date in the table 'product_descriptions'
        self.m_s_vendor_email = ''  # vendor_email in the table 'product_descriptions'
        # member variables for table 'vendor_profiles'
        self.m_s_vendor_profile = ''  # other variables exists above
        self.m_s_terms_conditions = ''
        self.m_s_join_date_member_since = ''
        self.m_s_last_active_date = ''
        self.m_s_pgp = ''
        self.m_n_num_orders_completed = -1
        self.m_n_num_orders_open = -1
        self.m_f_total_revenue = -1
        self.m_n_vendor_level = -1
        self.m_n_trust_level = -1
        self.m_n_trust_seller_yes_or_no = -1  # 0 no; 1 yes; -1, missing
        self.m_n_num_trust_yes = -1
        self.m_n_num_trust_no = -1
        self.m_f_avg_ratings = -1
        self.m_n_num_ratings = -1
        self.m_n_num_ratings_positive = -1
        self.m_n_num_ratings_negative = -1
        self.m_n_num_ratings_neutral = -1
        self.m_n_num_disputes_won = -1
        self.m_n_num_disputes_lost = -1
        self.m_s_fe_enabled = ''
        self.m_s_ws_vendor_level = ''
        # member variables for remote SQL database server
        self.m_sServerHost = "jaguar.cs.gsu.edu"
        self.m_sServerUser = "scraper"
        self.m_sServerPasswd = "Im9nZe5l84RoL8r9f2no"
        self.m_sServerDatabaseUser = "parser"
        self.m_sServerDatabasePasswd = "WHlNX941jZMSdwJSD7GY"
        self.m_sServerDatabaseRawHTMLs = "cryptomarkets"
        self.m_sServerDatabaseParsed = "cryptmktdb_parsed"
        self.m_sServerPort = "3306"
        self.m_bServerSQLBuffered = True
        # member variables for html file names
        self.m_s_html_file_name_pr = ''
        self.m_s_html_file_name_pd = ''
        self.m_s_html_file_name_vp = ''
        self.m_s_html_file_name_vr = ''
        self.m_s_local_directory = '/home/rob/temp_html_parsing/'
        self.m_s_local_file_name_vr = ''
        self.m_s_local_file_name_vp = ''
        self.m_s_local_file_name_pd = ''
        self.m_s_local_file_name_pr = ''
        # member variables for remote root directory in the file system of the server OS of the raw htmls db
        self.m_sRemoteRootDirectoryProductDesc = ""
        self.m_sRemoteRootDirectoryProductRating = ""
        self.m_sRemoteRootDirectoryVendorProfile = ""
        self.m_sRemoteRootDirectoryVendorRating = ""

    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)

    def select_root_directories_of_one_market(self):
        # query root directory of one market specified by 'self.m_n_cryptomarket_global_ID'
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch market information
        aSelectStmt_cryptomarkets_list = "SELECT * FROM cryptomarkets_list WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt_cryptomarkets_list)
        if aCursorDB_cryptomarkets.rowcount == 1:
            aOneMarketRecord = aCursorDB_cryptomarkets.fetchone()
            self.m_sRemoteRootDirectoryProductDesc = aOneMarketRecord["product_desc_root_directory"]
            self.m_sRemoteRootDirectoryProductRating = aOneMarketRecord["product_rating_root_directory"]
            self.m_sRemoteRootDirectoryVendorProfile = aOneMarketRecord["vendor_profile_root_directory"]
            self.m_sRemoteRootDirectoryVendorRating = aOneMarketRecord["vendor_rating_root_directory"]
        aMariaDB_cryptomarkets.close()

    def select_last_parsed_scraping_event_IDs(self):
        # query last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aSelectStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        # Fetch the information
        aSelectStmt_parser_progress = "SELECT * FROM parser_progress WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aSelectStmt_parser_progress)
        if aCursorDB_cryptmktdb_parsed.rowcount == 1:
            aOneRecord = aCursorDB_cryptmktdb_parsed.fetchone()
            self.m_n_last_parsed_scraping_event_ID_pd = aOneRecord["last_parsed_scraping_event_ID_pd"]
            self.m_n_last_parsed_scraping_event_ID_pd_4pr = aOneRecord["last_parsed_scraping_event_ID_pd_4pr"]
            self.m_n_last_parsed_scraping_event_ID_pr = aOneRecord["last_parsed_scraping_event_ID_pr"]
            self.m_n_last_parsed_scraping_event_ID_vp = aOneRecord["last_parsed_scraping_event_ID_vp"]
            self.m_n_last_parsed_scraping_event_ID_vp_4vr = aOneRecord["last_parsed_scraping_event_ID_vp_4vr"]
            self.m_n_last_parsed_scraping_event_ID_vr = aOneRecord["last_parsed_scraping_event_ID_vr"]
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_pd(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_pd = '" + str(
            self.m_n_last_parsed_scraping_event_ID_pd) + "' " \
                                                         "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_pd_4pr(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_pd_4pr = '" + str(
            self.m_n_last_parsed_scraping_event_ID_pd_4pr) + "' " \
                                                             "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_pr(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_pr = '" + str(
            self.m_n_last_parsed_scraping_event_ID_pr) + "' " \
                                                         "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_vp(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_vp = '" + str(
            self.m_n_last_parsed_scraping_event_ID_vp) + "' " \
                                                         "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_vp_4vr(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_vp_4vr = '" + str(
            self.m_n_last_parsed_scraping_event_ID_vp_4vr) + "' " \
                                                             "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def update_last_parsed_scraping_event_ID_vr(self):
        # update last parsed scraping event IDs
        # 20190704 YW add "WHERE" condition in "aUpdateStmt_parser_progress"
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aUpdateStmt_parser_progress = "UPDATE parser_progress SET " \
                                      "last_parsed_scraping_event_ID_vr = '" + str(
            self.m_n_last_parsed_scraping_event_ID_vr) + "' " \
                                                         "WHERE cryptomarket_global_ID='" + str(
            self.m_n_cryptomarket_global_ID) + "';"
        aCursorDB_cryptmktdb_parsed.execute(aUpdateStmt_parser_progress)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def insert_one_product_rating(self):
        # Insert one product rating to the product_ratings table in the cryptmktdb_parsed SQL database
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aMariaDB_cryptmktdb_parsed.set_charset_collation('utf8mb4', 'utf8mb4_general_ci')
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aInsertStmt_product_rating = (
            "INSERT INTO product_ratings (cryptomarket_global_ID, vendor_global_ID, vendor_market_ID, vendor_market_name, "
            "buyer_market_ID, rating_stars, text_comments, post_date, scraping_date, money_bitcoin, money_monero, money_usd, money_eur, "
            "buyer_total_num_of_orders, buyer_total_value_of_orders, product_global_ID, product_market_ID, product_title) "
            "VALUES (%(cryptomarket_global_ID)s, %(vendor_global_ID)s, %(vendor_market_ID)s, %(vendor_market_name)s, "
            "%(buyer_market_ID)s, %(rating_stars)s, %(text_comments)s, %(post_date)s,%(scraping_date)s, %(money_bitcoin)s, %(money_monero)s, %(money_usd)s, %(money_eur)s, "
            "%(buyer_total_num_of_orders)s, %(buyer_total_value_of_orders)s, %(product_global_ID)s, %(product_market_ID)s, %(product_title)s)")
        aData_product_rating = {
            'cryptomarket_global_ID': self.m_n_cryptomarket_global_ID,
            'vendor_global_ID': self.m_n_vendor_global_ID,
            'vendor_market_ID': self.m_s_vendor_market_ID,
            'vendor_market_name': self.m_s_vendor_market_name,
            'buyer_market_ID': self.m_s_buyer_market_ID,
            'rating_stars': self.m_f_rating_stars,
            'text_comments': self.m_s_text_comments,
            'post_date': self.m_s_post_date,
            'scraping_date': self.m_s_scraping_time,
            'money_bitcoin': self.m_f_money_bitcoin,
            'money_monero': self.m_f_money_monero,
            'money_usd': self.m_f_money_usd,
            'money_eur': self.m_f_money_eur,
            'buyer_total_num_of_orders': self.m_n_buyer_total_num_of_orders,
            'buyer_total_value_of_orders': self.m_f_buyer_total_value_of_orders,
            'product_global_ID': self.m_n_product_global_ID,
            'product_market_ID': self.m_s_product_market_ID,
            'product_title': self.m_s_product_title,
        }
        aCursorDB_cryptmktdb_parsed.execute(aInsertStmt_product_rating, aData_product_rating)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def insert_one_vendor_rating(self):
        # Insert one vendor rating to the vendor_ratings table in the cryptmktdb_parsed SQL database
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aMariaDB_cryptmktdb_parsed.set_charset_collation('utf8mb4', 'utf8mb4_general_ci')
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aInsertStmt_vendor_rating = (
            "INSERT INTO vendor_ratings (cryptomarket_global_ID, vendor_global_ID, vendor_market_ID, vendor_market_name, "
            "buyer_market_ID, rating_stars, text_comments, post_date, money_bitcoin, money_monero, money_usd, money_eur, "
            "buyer_total_num_of_orders, buyer_total_value_of_orders, product_market_ID, product_title) "
            "VALUES (%(cryptomarket_global_ID)s, %(vendor_global_ID)s, %(vendor_market_ID)s, %(vendor_market_name)s, "
            "%(buyer_market_ID)s, %(rating_stars)s, %(text_comments)s, %(post_date)s, %(money_bitcoin)s, %(money_monero)s, %(money_usd)s, %(money_eur)s, "
            "%(buyer_total_num_of_orders)s, %(buyer_total_value_of_orders)s, %(product_market_ID)s, %(product_title)s)")
        aData_vendor_rating = {
            'cryptomarket_global_ID': self.m_n_cryptomarket_global_ID,
            'vendor_global_ID': self.m_n_vendor_global_ID,
            'vendor_market_ID': self.m_s_vendor_market_ID,
            'vendor_market_name': self.m_s_vendor_market_name,
            'buyer_market_ID': self.m_s_buyer_market_ID,
            'rating_stars': self.m_f_rating_stars,
            'text_comments': self.m_s_text_comments,
            'post_date': self.m_s_post_date,
            'money_bitcoin': self.m_f_money_bitcoin,
            'money_monero': self.m_f_money_monero,
            'money_usd': self.m_f_money_usd,
            'money_eur': self.m_f_money_eur,
            'buyer_total_num_of_orders': self.m_n_buyer_total_num_of_orders,
            'buyer_total_value_of_orders': self.m_f_buyer_total_value_of_orders,
            'product_market_ID': self.m_s_product_market_ID,
            'product_title': self.m_s_product_title,
        }
        aCursorDB_cryptmktdb_parsed.execute(aInsertStmt_vendor_rating, aData_vendor_rating)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def insert_one_product_description(self):
        # Insert one product description to the product_descriptions table in the cryptmktdb_parsed SQL database
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)  # charset='utf8'
        aMariaDB_cryptmktdb_parsed.set_charset_collation('utf8mb4', 'utf8mb4_general_ci')
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aInsertStmt_product_desc = (
            "INSERT INTO product_descriptions (scraping_time, cryptomarket_global_ID, product_global_ID, "
            "vendor_global_ID, vendor_market_ID, vendor_market_name, product_title, product_desc, price_usd, price_eur, price_bitcoin, "
            "ships_to, ships_from, escrow, category, num_sales, num_stock, "
            "quantity_in_stock, min_amount_per_order, max_amount_per_order, already_sold, num_views, ads_post_date, vendor_email) "
            "VALUES (%(scraping_time)s, %(cryptomarket_global_ID)s, %(product_global_ID)s, "
            "%(vendor_global_ID)s, %(vendor_market_ID)s, %(vendor_market_name)s, %(product_title)s, %(product_desc)s, %(price_usd)s, %(price_eur)s, %(price_bitcoin)s, "
            "%(ships_to)s, %(ships_from)s, %(escrow)s, %(category)s, %(num_sales)s, %(num_stock)s, "
            "%(quantity_in_stock)s, %(min_amount_per_order)s, %(max_amount_per_order)s, %(already_sold)s, %(num_views)s, %(ads_post_date)s, %(vendor_email)s)")
        aData_product_desc = {
            'scraping_time': self.m_s_scraping_time,  #
            'cryptomarket_global_ID': self.m_n_cryptomarket_global_ID,  #
            'product_global_ID': self.m_n_product_global_ID,  #
            'vendor_global_ID': self.m_n_vendor_global_ID,  #
            'vendor_market_ID': self.m_s_vendor_market_ID,  #
            'vendor_market_name': self.m_s_vendor_market_name,  #
            'product_title': self.m_s_product_title,  #
            'product_desc': self.m_s_product_desc,  #
            'price_usd': self.m_f_price_usd,  #
            'price_eur': self.m_f_price_eur,  #
            'price_bitcoin': self.m_f_price_bitcoin,  #
            'ships_to': self.m_s_ships_to,  #
            'ships_from': self.m_s_ships_from,  #
            'escrow': self.m_s_escrow,  #
            'category': self.m_s_category,  #
            'num_sales': self.m_n_num_sales,  #
            'num_stock': self.m_n_num_stock,  #
            'quantity_in_stock': self.m_s_quantity_in_stock,  #
            'min_amount_per_order': self.m_s_min_amount_per_order,  #
            'max_amount_per_order': self.m_s_max_amount_per_order,  #
            'already_sold': self.m_s_already_sold,  #
            'num_views': self.m_n_num_views,  #
            'ads_post_date': self.m_s_ads_post_date,  #
            'vendor_email': self.m_s_vendor_email  #
        }
        aCursorDB_cryptmktdb_parsed.execute(aInsertStmt_product_desc, aData_product_desc)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def insert_one_vendor_profile(self):
        # Insert one vendor profile to the vendor_profiles table in the cryptmktdb_parsed SQL database
        aMariaDB_cryptmktdb_parsed = mysql.connector.connect(host=self.m_sServerHost,
                                                             user=self.m_sServerDatabaseUser,
                                                             passwd=self.m_sServerDatabasePasswd,
                                                             database=self.m_sServerDatabaseParsed,
                                                             port=self.m_sServerPort,
                                                             buffered=self.m_bServerSQLBuffered)
        aMariaDB_cryptmktdb_parsed.set_charset_collation('utf8mb4', 'utf8mb4_general_ci')
        aCursorDB_cryptmktdb_parsed = aMariaDB_cryptmktdb_parsed.cursor(dictionary=True)
        aInsertStmt_vendor_profile = (
            "INSERT INTO vendor_profiles (scraping_time, cryptomarket_global_ID, vendor_global_ID, "
            "vendor_market_ID, vendor_market_name, vendor_profile, terms_conditions, join_date_member_since, last_active_date, "
            "pgp, num_orders_completed, num_orders_open, total_revenue, vendor_level, trust_level,"
            "trust_seller_yes_or_no, num_trust_yes, num_trust_no, avg_ratings, num_ratings, "
            "num_ratings_positive, num_ratings_negative, num_ratings_neutral, num_disputes_won, num_disputes_lost, fe_enabled, ws_vendor_level) "
            "VALUES (%(scraping_time)s, %(cryptomarket_global_ID)s, %(vendor_global_ID)s, "
            "%(vendor_market_ID)s, %(vendor_market_name)s, %(vendor_profile)s, %(terms_conditions)s, %(join_date_member_since)s, %(last_active_date)s, "
            "%(pgp)s, %(num_orders_completed)s, %(num_orders_open)s, %(total_revenue)s, %(vendor_level)s, %(trust_level)s,"
            "%(trust_seller_yes_or_no)s, %(num_trust_yes)s, %(num_trust_no)s, %(avg_ratings)s, %(num_ratings)s, "
            "%(num_ratings_positive)s, %(num_ratings_negative)s, %(num_ratings_neutral)s, %(num_disputes_won)s, %(num_disputes_lost)s, %(fe_enabled)s, %(ws_vendor_level)s)")
        aData_vendor_profile = {
            'scraping_time': self.m_s_scraping_time,
            'cryptomarket_global_ID': self.m_n_cryptomarket_global_ID,
            'vendor_global_ID': self.m_n_vendor_global_ID,
            'vendor_market_ID': self.m_s_vendor_market_ID,
            'vendor_market_name': self.m_s_vendor_market_name,
            'vendor_profile': self.m_s_vendor_profile,
            'terms_conditions': self.m_s_terms_conditions,
            'join_date_member_since': self.m_s_join_date_member_since,
            'last_active_date': self.m_s_last_active_date,
            'pgp': self.m_s_pgp,
            'num_orders_completed': self.m_n_num_orders_completed,
            'num_orders_open': self.m_n_num_orders_open,
            'total_revenue': self.m_f_total_revenue,
            'vendor_level': self.m_n_vendor_level,
            'trust_level': self.m_n_trust_level,
            'trust_seller_yes_or_no': self.m_n_trust_seller_yes_or_no,
            'num_trust_yes': self.m_n_num_trust_yes,
            'num_trust_no': self.m_n_num_trust_no,
            'avg_ratings': self.m_f_avg_ratings,
            'num_ratings': self.m_n_num_ratings,
            'num_ratings_positive': self.m_n_num_ratings_positive,
            'num_ratings_negative': self.m_n_num_ratings_negative,
            'num_ratings_neutral': self.m_n_num_ratings_neutral,
            'num_disputes_won': self.m_n_num_disputes_won,
            'num_disputes_lost': self.m_n_num_disputes_lost,
            'fe_enabled': self.m_s_fe_enabled,
            'ws_vendor_level': self.m_s_ws_vendor_level
        }
        aCursorDB_cryptmktdb_parsed.execute(aInsertStmt_vendor_profile, aData_vendor_profile)
        aMariaDB_cryptmktdb_parsed.commit()
        aMariaDB_cryptmktdb_parsed.close()

    def parse_one_html_product_ratings(self):  # each cryptomarket parser need to implement this function
        pass

    def parse_one_html_vendor_ratings(self):  # each cryptomarket parser need to implement this function
        pass

    def parse_one_html_product_descriptions(self):  # each cryptomarket parser need to implement this function
        pass

    def parse_one_html_vendor_profiles(self):  # each cryptomarket parser need to implement this function
        pass

    def query_vendor_list_by_vendor_global_ID(self, n_vendor_global_ID):
        # query the vendor_list table by using the vendor_global_ID attribute:
        # select * from vendor_list where vendor_global_ID = n_vendor_global_ID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM vendor_list WHERE vendor_global_ID = '" + str(n_vendor_global_ID) + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
        n_cryptomarket_global_ID = aOneVendorRecord['cryptomarket_global_ID']
        s_vendor_market_ID = aOneVendorRecord['vendor_market_ID']
        aMariaDB_cryptomarkets.close()
        return [n_cryptomarket_global_ID, s_vendor_market_ID]

    def query_vendor_list_by_vendor_market_ID(self, n_cryptomarket_global_ID, s_vendor_market_ID):
        # query the vendor_list table by using the vendor_global_ID attribute:
        # select * from vendor_list where cryptomarket_global_ID = n_cryptomarket_global_ID and vendor_market_ID = s_vendor_market_ID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM vendor_list WHERE cryptomarket_global_ID = '" + str(
            n_cryptomarket_global_ID) + "' AND vendor_market_ID = '" + s_vendor_market_ID + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        if aCursorDB_cryptomarkets.rowcount > 0:
            aOneVendorRecord = aCursorDB_cryptomarkets.fetchone()
            n_vendor_global_ID = aOneVendorRecord['vendor_global_ID']
        else:
            n_vendor_global_ID = -1
            print('not found: %d, %s' % (n_cryptomarket_global_ID, s_vendor_market_ID))
        aMariaDB_cryptomarkets.close()
        return n_vendor_global_ID

    def query_product_list_by_product_global_ID(self, n_product_global_ID):
        # query the product_list table by using the product_global_ID attribute:
        # select * from product_list where product_global_ID = n_product_global_ID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM product_list WHERE product_global_ID = '" + str(n_product_global_ID) + "';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        if aCursorDB_cryptomarkets.rowcount > 0:
            aOneProductRecord = aCursorDB_cryptomarkets.fetchone()
            n_cryptomarket_global_ID = aOneProductRecord['cryptomarket_global_ID']
            s_product_market_ID = aOneProductRecord['product_market_ID']
        else:
            n_cryptomarket_global_ID = 0
            s_product_market_ID = ''
            print('not found product_global_ID: %d' % n_product_global_ID)
        aMariaDB_cryptomarkets.close()
        return [n_cryptomarket_global_ID, s_product_market_ID]

    def select_vendor_rating_scraping_event(self, n_last_parsed_scraping_event_ID_vr):
        # select * from vendor_rating_scraping_event where scraping_event_ID_vendor > self.m_n_last_parsed_scraping_event_ID_vr
        # AND cryptomarket_global_ID == OneMarketID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM vendor_rating_scraping_event " + \
                      "WHERE scraping_event_ID_vendor > '" + str(n_last_parsed_scraping_event_ID_vr) + "' " + \
                      "AND vendor_rating_file_path_in_FS REGEXP '^[0-9]{14}_" + str(
            self.m_n_cryptomarket_global_ID).zfill(2) + "_';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        vaVendorRatingScrapingEvents = aCursorDB_cryptomarkets.fetchall()
        aMariaDB_cryptomarkets.close()
        return vaVendorRatingScrapingEvents

    def select_vendor_profile_scraping_event(self, n_last_parsed_scraping_event_ID_vp):
        # select * from vendor_profile_scraping_event where scraping_event_ID_vendor > self.m_n_last_parsed_scraping_event_ID_vp
        # AND cryptomarket_global_ID == OneMarketID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM vendor_profile_scraping_event " + \
                      "WHERE scraping_event_ID_vendor > '" + str(n_last_parsed_scraping_event_ID_vp) + "' " + \
                      "AND vendor_profile_file_path_in_FS REGEXP '^[0-9]{14}_" + str(
            self.m_n_cryptomarket_global_ID).zfill(2) + "_';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        vaVendorProfileScrapingEvents = aCursorDB_cryptomarkets.fetchall()
        aMariaDB_cryptomarkets.close()
        return vaVendorProfileScrapingEvents

    def select_product_rating_scraping_event(self, n_last_parsed_scraping_event_ID_pr):
        # select * from product_rating_scraping_event where scraping_event_ID_product > self.m_n_last_parsed_scraping_event_ID_pr
        # AND cryptomarket_global_ID == OneMarketID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM product_rating_scraping_event " + \
                      "WHERE scraping_event_ID_product > '" + str(n_last_parsed_scraping_event_ID_pr) + "' " + \
                      "AND product_rating_file_path_in_FS REGEXP '^[0-9]{14}_" + str(
            self.m_n_cryptomarket_global_ID).zfill(2) + "_';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        vaProductRatingScrapingEvents = aCursorDB_cryptomarkets.fetchall()
        aMariaDB_cryptomarkets.close()
        return vaProductRatingScrapingEvents

    def select_product_desc_scraping_event(self, n_last_parsed_scraping_event_ID_pd):
        # select * from product_desc_scraping_event where scraping_event_ID_product > self.m_n_last_parsed_scraping_event_ID_pd
        # AND cryptomarket_global_ID == OneMarketID
        aMariaDB_cryptomarkets = mysql.connector.connect(host=self.m_sServerHost,
                                                         user=self.m_sServerDatabaseUser,
                                                         passwd=self.m_sServerDatabasePasswd,
                                                         database=self.m_sServerDatabaseRawHTMLs,
                                                         port=self.m_sServerPort,
                                                         buffered=self.m_bServerSQLBuffered)
        aCursorDB_cryptomarkets = aMariaDB_cryptomarkets.cursor(dictionary=True)
        # Fetch scraping event information
        aSelectStmt = "SELECT * FROM product_desc_scraping_event " + \
                      "WHERE scraping_event_ID_product > '" + str(n_last_parsed_scraping_event_ID_pd) + "' " + \
                      "AND product_desc_file_path_in_FS REGEXP '^[0-9]{14}_" + str(
            self.m_n_cryptomarket_global_ID).zfill(2) + "_';"
        aCursorDB_cryptomarkets.execute(aSelectStmt)
        vaProductDescScrapingEvents = aCursorDB_cryptomarkets.fetchall()
        aMariaDB_cryptomarkets.close()
        return vaProductDescScrapingEvents

    def TransferDaysAgoToAbsDateTime(self, sInputString):
        # convert some phrase like "17 hours ago" into a datetime object based on self.m_s_scraping_time
        a_post_date = None
        if ' minute ago' in sInputString:
            n_date_diff_min = 1
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                minutes=n_date_diff_min)
        elif ' minutes ago' in sInputString:
            n_date_diff_min = int(sInputString[:sInputString.index(' minutes ago')])
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                minutes=n_date_diff_min)
        elif ' hour ago' in sInputString:
            n_date_diff_hour = 1
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                hours=n_date_diff_hour)
        elif ' hours ago' in sInputString:
            n_date_diff_hour = int(sInputString[:sInputString.index(' hours ago')])
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                hours=n_date_diff_hour)
        elif ' day ago' in sInputString:
            n_date_diff_day = 1
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        elif ' days ago' in sInputString:
            n_date_diff_day = int(sInputString[:sInputString.index(' days ago')])
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        elif ' week ago' in sInputString:
            n_date_diff_week = 7
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                weeks=n_date_diff_week)
        elif ' weeks ago' in sInputString:
            n_date_diff_week = int(sInputString[:sInputString.index(' weeks ago')]) * 7
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                weeks=n_date_diff_week)
        elif ' month ago' in sInputString:
            n_date_diff_day = 30
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        elif ' months ago' in sInputString:
            n_date_diff_day = int(sInputString[:sInputString.index(' months ago')]) * 30
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        elif ' year ago' in sInputString:
            n_date_diff_day = 365
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        elif ' years ago' in sInputString:
            n_date_diff_day = int(sInputString[:sInputString.index(' years ago')]) * 365
            a_post_date = datetime.datetime.strptime(self.m_s_scraping_time, "%Y%m%d%H%M%S") - datetime.timedelta(
                days=n_date_diff_day)
        else:
            print('tp date not processed' + sInputString)
            a_post_date = datetime.datetime.fromtimestamp(0)
        return a_post_date