import os
from bs4 import BeautifulSoup
from parser_base import parser_base


class parser_darkfox(parser_base):
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
            self.m_s_product_title = aBeautifulSoup.findChild('h1').text[:255]
            print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

        # ########## Category ##########
        try:
            self.m_s_category = aBeautifulSoup.findAll('ul', {'class': 'has-text-left m-l-md'})[1].findAll('li')[
                1].find('span', {'class': 'tag is-dark'}).text
            print('PC: ', self.m_s_category)
        except Exception as e:
            print('Not Found: Category', str(e))

        # ########## Price ##########
        try:
            priceText = aBeautifulSoup.findAll('strong')[0].text
            self.m_f_price_usd = float(priceText)
            self.m_s_min_amount_per_order = priceText.strip()
            print('P1: ', self.m_f_price_usd)
            print('p2: ', self.m_s_min_amount_per_order)
        except Exception as e:
            print('Not Found: Price', str(e))

        # ########## Vendor Info ##########
        try:
            self.m_s_vendor_market_ID = aBeautifulSoup.findAll('h3')[0].find('a').text

            self.m_s_vendor_market_name = aBeautifulSoup.findAll('h3')[0].find('a').text
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('Vendor:', self.m_s_vendor_market_name)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))

        # ########## Product Description ##########
        try:
            self.m_s_product_desc = aBeautifulSoup.find('div', {'class', 'pre-line'}).text[:511]

            print('Product description:', self.m_s_product_desc)
            # Check for other product description files and append.
        except Exception as e:
            print('Not Found: Product Description', str(e))

            ########## Stock ##############
        try:
            self.m_n_num_stock = aBeautifulSoup.findAll('ul', {'class': 'has-text-left m-l-md'})[1].findAll('li')[
                3].find('span', {'class': 'tag is-dark'}).text
            self.m_n_num_stock = int(self.m_n_num_stock)
            print('Stock :', self.m_n_num_stock)
        except Exception as e:
            print('Not Found: Ships from', str(e))

            ######### Sales #############
        try:
            self.m_n_num_sales = aBeautifulSoup.findAll('ul', {'class': 'has-text-left m-l-md'})[1].findAll('li')[
                4].find('span', {'class': 'tag is-dark'}).text
            self.m_n_num_sales = int(self.m_n_num_sales)
            print('Sales :', self.m_n_num_sales)
        except Exception as e:
            print('Not Found: Ships from', str(e))

            ######### Escrow ############
        try:
            escrow = aBeautifulSoup.findAll('ul', {'class': 'has-text-left m-l-md'})[1].findAll('li')[1].find('span', {
                'class': 'tag is-dark'}).text
            if escrow == "normal":
                self.m_s_escrow = "Yes"
            else:
                self.m_s_escrow = "No"
            print('Escrow :', self.m_s_escrow)
        except Exception as e:
            print('Not Found: Ships from', str(e))

        # No info available for the following
        self.m_f_price_eur = -1
        self.m_f_price_bitcoin = -1
        self.m_s_quantity_in_stock = ''
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_s_already_sold = ''
        self.m_n_num_views = 0
        self.m_s_ships_from = ''
        self.m_s_ads_post_date = ''  # ads_post_date in the table 'product_descriptions'
        self.m_s_vendor_email = ''

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
                self.m_s_product_title = aBeautifulSoup.findChild('h1').text[:255]
                print('PT: ', self.m_s_product_title)
            except Exception as e:
                print('Not Found: Product Title', str(e))

            # ########## Category ##########
            try:
                self.m_s_category = aBeautifulSoup.findAll('ul', {'class': 'has-text-left m-l-md'})[1].findAll('li')[
                    1].find('span', {'class': 'tag is-dark'}).text
                print('PC: ', self.m_s_category)
            except Exception as e:
                print('Not Found: Category', str(e))

            # ########## Price ##########
            try:
                priceText = aBeautifulSoup.findAll('strong')[0].text
                self.m_f_price_usd = float(priceText)
                self.m_s_min_amount_per_order = priceText.strip()
                print('P1: ', self.m_f_price_usd)
                print('p2: ', self.m_s_min_amount_per_order)
            except Exception as e:
                print('Not Found: Price', str(e))

            # ########## Vendor Info ##########
            try:
                self.m_s_vendor_market_ID = aBeautifulSoup.findAll('h3')[0].find('a').text

                self.m_s_vendor_market_name = aBeautifulSoup.findAll('h3')[0].find('a').text
                self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                       self.m_s_vendor_market_ID)
                print('VID: ', self.m_n_vendor_global_ID)
                print('Vendor:', self.m_s_vendor_market_name)
            except Exception as e:
                print('Not Found: Vendor Info', str(e))

            # Feedback Table
            reviewsTable = aBeautifulSoup.find('table', {'class': 'table table-compact table-no-margin'})
            if reviewsTable:
                # print('Table Present')
                reviewCounttable = aBeautifulSoup.findAll('table', {
                    'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('tr')[5]
                reviewCount = reviewCounttable.find('td').findAll('a')[0].find('span').text
                print('Review Count: ', int(reviewCount))
                allReviewRows = reviewsTable.find('tbody').findAll('tr')
                if int(reviewCount) > 0:
                    for reviewRow in allReviewRows:
                        # Feedback type
                        self.m_f_rating_stars = reviewRow.findAll('td')[1].find('span',
                                                                                {'class': 'label label-success'}).text
                        print('Feedback type: ', self.m_f_rating_stars)
                        self.m_s_text_comments = reviewRow.findAll('td')[2].text
                        print('Comment: ', self.m_s_text_comments)
                else:
                    print('No Reviews Yet.')
            self.insert_one_product_rating()
        except Exception as e:
            # print(self.m_s_local_file_name_pr)
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

            #self.m_s_vendor_profile = aBeautifulSoup.find('div', {'class': 'message-body'}).find('div').text
            #print('Profile:', self.m_s_vendor_profile)

            # Extract join date
            self.m_s_join_date_member_since = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[5].text
            print('Joined Date', self.m_s_join_date_member_since)

            # Extract Last Active Date
            self.m_s_last_active_date = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[1].text
            print('Last Active Date', self.m_s_last_active_date)

            # Extract Vendor Level
            self.m_n_vendor_level = \
            aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[6].find('span').text.split('Vendor Level ')[1]
            print('Vendor Level', self.m_n_vendor_level)

            # Extract Orders completed
            self.m_n_num_orders_completed = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[7].text
            print('Orders Completed', self.m_n_num_orders_completed)

            # Extract disputes won
            self.m_n_num_disputes_won = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[8].findAll('font')[0].text

            print('Disputes won',self.m_n_num_disputes_won)

            # Extract disputes lost
            self.m_n_num_disputes_lost = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[8].findAll('font')[1].text
            print('Disputes lost', self.m_n_num_disputes_lost)

            # Extract Average Rating
            self.m_f_avg_ratings = aBeautifulSoup.findAll('font', {'class': 'is-pulled-right'})[9].findAll('span')[
                5].text
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
            print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = self.m_s_local_file_name_vr.split('_')[-2]
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)

            total_num_of_reviews = 0

            reviewsTable = aBeautifulSoup.findAll('div', {'class': 'box has-text-centered break-all'})[0].findAll('div', {'class' :'columns m-b-none'})
            for reviewRow in reviewsTable:
                self.m_s_text_comments = reviewRow.findAll('div')[1].find('i').text.strip()
                print('Comments:', self.m_s_text_comments)

                self.m_f_rating_stars = reviewRow.findAll('div')[0].findAll('span')[5].text.split('.')[0]

                print('Rating:', self.m_f_rating_stars)
                        # Product title
                self.m_s_product_title = reviewRow.findAll('div')[1].find('p').find('a').text.strip()
                print('Product:', self.m_s_product_title)

                # Date
                self.m_s_post_date = reviewRow.findAll('div')[3].text.strip()
                print('Date: ', self.m_s_post_date)
                        # Insert this rating to the db
                self.insert_one_vendor_rating()

        except Exception as e:
            print('Not Found: Vendor Ratings.', str(e))
