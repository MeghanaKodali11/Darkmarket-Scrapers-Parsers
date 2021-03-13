import os
from bs4 import BeautifulSoup
from parser_base import parser_base


class parser_corona(parser_base):
    def parse_one_html_product_descriptions(self):
        # Input: html file 'self.m_s_html_file_name_pd' (remote),
        # Output: table 'product_desc' in db 'cryptmktdb_parsed'
        # Download the file from the sever
        sSCP_Command = "sshpass -p '{}' scp {}@{}:{} {}".format(self.m_sServerPasswd, self.m_sServerUser,
                                                                self.m_sServerHost, self.m_s_html_file_name_pd,
                                                                self.m_s_local_directory)
        os.system(sSCP_Command)

        if not os.path.isfile(self.m_s_local_file_name_pd):
            print('File not found...')
            return

        aOneProductsDescPage = open(self.m_s_local_file_name_pd, encoding='utf-8')
        aBeautifulSoup = BeautifulSoup(aOneProductsDescPage, features="html.parser")
        aOneProductsDescPage.close()
        os.remove(self.m_s_local_file_name_pd)

        # ########## product title ##########
        try:
            self.m_s_product_title = aBeautifulSoup.findChild('div', {'class':'title is-3 has-text-centered'}).text[:255]
            print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

        # ########## Category ##########
        try:
            self.m_s_category = aBeautifulSoup.find('div', {'class': 'breadcrumb'}).find('ul').findAll('li')[0].findChild('a').text.strip()
            print('PC: ', self.m_s_category)
        except Exception as e:
            print('Not Found: Category', str(e))

        # ########## Price ##########
        try:
            priceText = aBeautifulSoup.findAll('option')[0].text.strip().split()[1]
            self.m_f_price_usd = float(priceText)
            self.m_s_min_amount_per_order = priceText.strip()
            print('P1: ', self.m_f_price_usd)
            print('p2: ', self.m_s_min_amount_per_order)
        except Exception as e:
            print('Not Found: Price', str(e))

        # ########## Vendor Info ##########
        try:
            self.m_s_vendor_market_ID = aBeautifulSoup.findAll('div',{'class':'level-item'})[0].find('div').findChild('a').text.strip()

            self.m_s_vendor_market_name = self.m_s_vendor_market_ID
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('Vendor:', self.m_s_vendor_market_name)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))


            ######### Sales  #############
        try:
            self.m_n_num_sales = aBeautifulSoup.find('div', {'class': 'tag is-info'}).text.partition('Sold: ')[2]
            self.m_n_num_sales = int(self.m_n_num_sales)
            print('Sales :', self.m_n_num_sales)
        except Exception as e:
            print('Not Found: Sales', str(e))

        ########## Views ##############
        try:
            self.m_n_num_views = aBeautifulSoup.find('span',{'class':'tag is-right'}).text.partition('Views: ')[2]
            self.m_n_num_views = int(self.m_n_num_views)
            print('Views', self.m_n_num_views)
        except Exception as e:
            print('Not Found: Views', str(e))

        # No info available for the following
        self.m_f_price_eur = -1
        self.m_f_price_bitcoin = -1
        self.m_s_quantity_in_stock = ''
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_s_already_sold = ''
        self.m_s_ads_post_date = ''  # ads_post_date in the table 'product_descriptions'
        self.m_s_vendor_email = ''
        self.m_s_escrow = "Yes"
        self.m_s_ships_to = ''
        self.m_s_ships_from = ''

        # ########## Insert into Database ##########
        self.insert_one_product_description()

    def parse_one_html_product_ratings(self):  # must implement this function
        # Input: html file 'self.m_s_html_file_name_pr' (remote),
        # Output: table 'product_ratings' in db 'cryptmktdb_parsed'
        # Download the file from the sever
        sSCP_Command = "sshpass -p '{}' scp {}@{}:{} {}".format(self.m_sServerPasswd, self.m_sServerUser,
                                                                self.m_sServerHost, self.m_s_html_file_name_pr,
                                                                self.m_s_local_directory)
        os.system(sSCP_Command)
        if not os.path.isfile(self.m_s_local_file_name_pr):
            print('File not found...')
            return

        aOneProductRatingPage = open(self.m_s_local_file_name_pr, encoding='utf-8')
        aBeautifulSoup = BeautifulSoup(aOneProductRatingPage, features="html.parser")
        aOneProductRatingPage.close()
        os.remove(self.m_s_local_file_name_pr)

        try:

            # ########## product title ##########
            try:
                self.m_s_product_title = aBeautifulSoup.findChild('div',
                                                                  {'class': 'title is-3 has-text-centered'}).text[:255]
                print('PT: ', self.m_s_product_title)
            except Exception as e:
                print('Not Found: Product Title', str(e))

            # ########## Category ##########
            try:
                self.m_s_category = aBeautifulSoup.find('div', {'class': 'breadcrumb'}).find('ul').findAll('li')[0].findChild('a').text.strip()
                print('PC: ', self.m_s_category)
            except Exception as e:
                print('Not Found: Category', str(e))

            # ########## Price ##########
            try:
                priceText = aBeautifulSoup.findAll('option')[0].text.strip().split()[1]
                self.m_f_price_usd = float(priceText)
                self.m_s_min_amount_per_order = priceText.strip()
                print('P1: ', self.m_f_price_usd)
                print('p2: ', self.m_s_min_amount_per_order)
            except Exception as e:
                print('Not Found: Price', str(e))
            # ########## Vendor Info ##########
            try:
                self.m_s_vendor_market_ID = aBeautifulSoup.findAll('div', {'class': 'level-item'})[0].find(
                    'div').findChild('a').text.strip()

                self.m_s_vendor_market_name = self.m_s_vendor_market_ID
                self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                       self.m_s_vendor_market_ID)
                print('VID: ', self.m_n_vendor_global_ID)
                print('Vendor:', self.m_s_vendor_market_name)
            except Exception as e:
                print('Not Found: Vendor Info', str(e))

            reviewsTable = aBeautifulSoup.findAll('div', {'class': 'message-body'})
            reviewCount = len(reviewsTable)
            print('Review Count:', reviewCount)
            for reviewRow in reviewsTable:
                self.m_s_text_comments = reviewRow.text.partition('★')[2][1:].strip()
                print('Comments:', self.m_s_text_comments)

                self.m_s_post_date = reviewRow.text.partition('★')[0].strip()
                print('Date: ', self.m_s_post_date)

                self.m_f_rating_stars = reviewRow.text.partition('★')[2][0]
                print('Rating:', self.m_f_rating_stars)

                self.insert_one_product_rating()
        except Exception as e:
            print('Exception: ', str(e))

    def parse_one_html_vendor_profiles(self):
        # Input: html file 'self.m_s_html_file_name_vp' (remote),
        # Output: table 'vendor_profiles' in db 'cryptmktdb_parsed'
        # Download the file from the sever
        sSCP_Command = "sshpass -p '{}' scp {}@{}:{} {}".format(self.m_sServerPasswd, self.m_sServerUser,
                                                                self.m_sServerHost, self.m_s_html_file_name_vp,
                                                                self.m_s_local_directory)
        os.system(sSCP_Command)
        if not os.path.isfile(self.m_s_local_file_name_vp):
            print('File not found...')
            return

        aOneVendorProfilePage = open(self.m_s_local_file_name_vp, encoding='utf-8')
        aBeautifulSoup = BeautifulSoup(aOneVendorProfilePage, features="html.parser")
        aOneVendorProfilePage.close()
        os.remove(self.m_s_local_file_name_vp)

        try:
            ########## Vendor Info ##########
            self.m_s_vendor_market_ID = self.m_s_local_file_name_vp.split('_')[-2]
            print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = self.m_s_local_file_name_vp.split('_')[-2]
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)


            # Extract join date
            self.m_s_join_date_member_since = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[1].find('div').find('div', {'class': 'title'}).text
            print('Joined Date', self.m_s_join_date_member_since)

            # Extract Last Active Date
            self.m_s_last_active_date = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[2].find('div').find('div', {'class': 'title'}).text
            print('Last Active Date', self.m_s_last_active_date)


            # Extract Orders completed
            num_orders_completed = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[6]
            self.m_n_num_orders_completed = num_orders_completed.find('div').find('span', {'class': 'title'}).text
            self.m_n_num_orders_completed = int(self.m_n_num_orders_completed)
            print('Orders Completed', self.m_n_num_orders_completed)

            # Extract disputes won
            self.m_n_num_disputes_won = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[9].find('div').find('span', {'class': 'title'}).text.partition('/')[0].strip()

            print('Disputes won',self.m_n_num_disputes_won)

            # Extract disputes lost
            self.m_n_num_disputes_lost = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[9].find('div').find('span', {'class': 'title'}).text.partition('/')[2].strip()
            print('Disputes lost', self.m_n_num_disputes_lost)

            # Extract Average Rating
            self.m_f_avg_ratings = aBeautifulSoup.findAll('div', {'class': 'level-item has-text-centered'})[0].find('div').find('div', {'class': 'title'}).text

            self.m_f_avg_ratings = float(self.m_f_avg_ratings)
            print('Average Rating', self.m_f_avg_ratings)


            # No info available for the following
            self.m_n_num_ratings_neutral = '0'
            self.m_n_num_ratings = '0'
            self.m_n_num_ratings_positive ='0'
            self.m_n_num_ratings_negative = '0'
            self.m_s_terms_conditions = ''
            self.m_n_num_orders_open = -1
            self.m_s_pgp = ''
            self.m_f_total_revenue = -1
            self.m_n_trust_level = -1
            self.m_n_trust_seller_yes_or_no = -1  # 0 no; 1 yes; -1, missing
            self.m_n_num_trust_yes = -1
            self.m_n_num_trust_no = -1
            self.m_s_fe_enabled = ''
            self.m_s_ws_vendor_level = ''
            #Insert this rating to the db
            self.insert_one_vendor_profile()
        except Exception as e:
            # print(self.m_s_local_file_name_pr)
            print('Exception: ', str(e))

    def parse_one_html_vendor_ratings(self):
        # Download the file from the sever
        sSCP_Command = "sshpass -p '{}' scp {}@{}:{} {}".format(self.m_sServerPasswd, self.m_sServerUser,
                                                                self.m_sServerHost, self.m_s_html_file_name_vr,
                                                                self.m_s_local_directory)
        os.system(sSCP_Command)
        if not os.path.isfile(self.m_s_local_file_name_vr):
            print('File not found...')
            return

        aOneVendorsRatingPage = open(self.m_s_local_file_name_vr, encoding='utf-8')
        aBeautifulSoup = BeautifulSoup(aOneVendorsRatingPage, features="html.parser")
        aOneVendorsRatingPage.close()
        os.remove(self.m_s_local_file_name_vr)

        try:
            ########## Vendor Info ##########
            self.m_s_vendor_market_ID = self.m_s_local_file_name_vr.split('_')[-2]
            print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = self.m_s_local_file_name_vr.split('_')[-2]
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)


            reviewsTable = aBeautifulSoup.findAll('div', {'class': 'message-body'})
            for reviewRow in reviewsTable:
                self.m_s_text_comments = reviewRow.text.partition('★')[2][1:].strip()
                print('Comments:', self.m_s_text_comments)

                self.m_s_post_date = reviewRow.text.partition('★')[0].strip()
                print('Date: ', self.m_s_post_date)

                self.m_f_rating_stars = reviewRow.text.partition('★')[2][0]
                print('Rating:', self.m_f_rating_stars)

                # Date

                # Insert this rating to the db
                self.insert_one_vendor_rating()

        except Exception as e:
            print('Not Found: Vendor Ratings.', str(e))