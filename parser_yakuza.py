import os
from bs4 import BeautifulSoup
from parser_base import parser_base


class parser_yakuza(parser_base):
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
            self.m_s_product_title = aBeautifulSoup.find('span', {'class': 'mb-2'}).text
            print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

        # ########## Category ##########
        try:
            self.m_s_category = aBeautifulSoup.findAll('li', {'class': 'breadcrumb-item'})[1].find('a').text
            print('PC: ', self.m_s_category)
        except Exception as e:
            print('Not Found: Category', str(e))

        # ########## Price ##########
        try:
            priceText = aBeautifulSoup.findAll('div', {'class': 'card-text'})[0].text
            price_usd = priceText.split('$')[1].split()[0].split(',')
            if len(price_usd) == 1:
                self.m_f_price_usd = float(price_usd[0])
            else:
                self.m_f_price_usd = float(price_usd[0] + price_usd[1])
            self.m_f_price_bitcoin = aBeautifulSoup.findAll('div', {'class': 'card-text'})[1].text.split()[1]
            self.m_f_price_bitcoin = float(self.m_f_price_bitcoin)
            self.m_s_min_amount_per_order = self.m_f_price_usd
            print('Price in USD: ', self.m_f_price_usd)
            print('Price in Bitcoin: ', self.m_f_price_bitcoin)
        except Exception as e:
            print('Not Found: Price', str(e))

            # ########## Product Quantity Available ##########
        try:
            quan = aBeautifulSoup.find('div', {'class', 'col-9'}).text
            self.m_s_quantity_in_stock = quan.split()[0]
            self.m_n_num_stock = self.m_s_quantity_in_stock
            print('Quantity in stock:', self.m_s_quantity_in_stock)
        except Exception as e:
            print('Not Found: Quantity', str(e))

        # ########## Product Description ##########
        try:
            self.m_s_product_desc = aBeautifulSoup.findAll('pre')[0].text[:1023]

            print('Product description:', self.m_s_product_desc)
            # Check for other product description files and append.
        except Exception as e:
            print('Not Found: Product Description', str(e))
        # ########## Vendor Info ##########
        try:
            self.m_s_vendor_market_ID = aBeautifulSoup.findAll('div', {'class': 'card-text'})[5].findAll('a')[
                0].text

            self.m_s_vendor_market_name = self.m_s_vendor_market_ID
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('Vendor:', self.m_s_vendor_market_name)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))

            ######### Sales #############
        try:
            self.m_n_num_sales = quan.split()[3]
            self.m_n_num_sales = int(self.m_n_num_sales)
            self.m_s_already_sold = self.m_n_num_sales
            print('Sales :', self.m_n_num_sales)
        except Exception as e:
            print('Not Found: Sales', str(e))

            # ########## Shipping info ##########
        try:
            self.m_s_ships_from = aBeautifulSoup.findAll('div', {'class', 'card-text'})[6].text.split()[2]
            self.m_s_ships_to = aBeautifulSoup.findAll('div', {'class', 'card-text'})[7].text.split()[2]
            print('Ships from:', self.m_s_ships_from)
            print('Ships to:', self.m_s_ships_to)
        except Exception as e:
            print('Not Found: Quantity', str(e))

        # No info available for the following
        self.m_f_price_eur = -1
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_n_num_views = 0
        self.m_s_ads_post_date = ''  # ads_post_date in the table 'product_descriptions'
        self.m_s_vendor_email = ''

        # ########## Insert into Database ##########

        self.insert_one_product_description()

#### There are no product ratings for this site

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

            self.m_s_vendor_market_name = self.m_s_local_file_name_vp.split('_')[-2]
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)

            # Extract join date
            self.m_s_join_date_member_since = aBeautifulSoup.find('ul', {'class': 'list-unstyled mt-3 mb-4'}).findAll('li')[2].text.split()[2]
            print('Joined Date', self.m_s_join_date_member_since)

            # Extract Orders completed
            self.m_n_num_orders_completed = aBeautifulSoup.find('ul', {'class': 'list-unstyled mt-3 mb-4'}).findAll('li')[4].text.split()[2]
            print('Orders Completed', self.m_n_num_orders_completed)

            # Extract disputes won
            self.m_n_num_disputes_won = aBeautifulSoup.find('span', {'class': 'badge badge-success'}).text.split()[1]

            print('Disputes won', self.m_n_num_disputes_won)

            # Extract disputes lost
            self.m_n_num_disputes_lost = aBeautifulSoup.find('span', {'class': 'badge badge-danger'}).text.split()[1]

            print('Disputes lost', self.m_n_num_disputes_lost)

            # No info available for the following
            self.m_n_num_ratings_neutral = '0'
            self.m_n_num_ratings = '0'
            self.m_f_avg_ratings = '0'
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
            self.m_n_vendor_level = '0'
            # Insert this rating to the db
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

            self.m_s_vendor_market_name = self.m_s_local_file_name_vr.split('_')[-2]
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)


            reviewsTable = aBeautifulSoup.find('table', {'class': 'table table-responsive'}).find('tbody').findAll('tr')
            if len(reviewsTable) != 0:
                for reviewRow in reviewsTable:
                    self.m_s_text_comments = reviewRow.findAll('td')[1].text.strip()
                    print('Comments:', self.m_s_text_comments)

                    #Product title
                    self.m_s_product_title = reviewRow.findAll('td')[3].text.strip()
                    print('Product:', self.m_s_product_title)

                    # Date
                    self.m_s_post_date = reviewRow.findAll('td')[4].text.strip()
                    print('Date: ', self.m_s_post_date)
                        # Insert this rating to the db
                    self.insert_one_vendor_rating()

        except Exception as e:
            print('Not Found: Vendor Ratings.', str(e))
