import os
from bs4 import BeautifulSoup
from parser_base import parser_base


class parser_liberty(parser_base):
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
            self.m_s_product_title = aBeautifulSoup.findChild('span',{'class':'text-left h3'}).text[:255]
            #print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

        ptable1 = aBeautifulSoup.findAll('table', {'class': 'table'})[0].find('tbody').findAll('tr')
        ptable2 = aBeautifulSoup.findAll('table', {'class': 'table'})[1].find('tbody').findAll('tr')

        # ########## Price ##########
        try:

            self.m_f_price_usd = float(ptable1[0].find('td').text.split('$')[0])
            self.m_s_min_amount_per_order = self.m_f_price_usd
            #print('P1: ', self.m_f_price_usd)
            #print('p2: ', self.m_s_min_amount_per_order)
        except Exception as e:
            print('Not Found: Price', str(e))

        # ########## Vendor Info ##########
        try:
            self.m_s_vendor_market_ID = aBeautifulSoup.find('a',{'class':'font-weight-bold liberty'}).text
            self.m_s_vendor_market_name = self.m_s_vendor_market_ID
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            #print('VID: ', self.m_n_vendor_global_ID)
            #print('Vendor:', self.m_s_vendor_market_name)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))

        # ########## Product Description ##########
        try:
            self.m_s_product_desc = aBeautifulSoup.find('pre', {'class', 'text-left full-text'}).text
            telegram = self.m_s_product_desc.split(' ')
            for i in range(len(telegram)):
                if '..' in telegram[i].lower():
                    tele = telegram[i].split('.')
                    print('telegram id =',tele[len(tele)-1].split()[0])
                    break


            #print('Product description:', self.m_s_product_desc)
        except Exception as e:
            print('Not Found: Product Description', str(e))

            ########## Ships from ##############
        try:
            self.m_s_ships_from = ptable2[2].find('td').text
            #print('Ships from :', self.m_s_ships_from)
        except Exception as e:
            print('Not Found: Ships from', str(e))

            ########## Ships to ##############
        try:
            self.m_s_ships_to = ptable2[3].find('td').text
            #print('Ships to:', self.m_s_ships_to)
        except Exception as e:
            print('Not Found: Ships to', str(e))

            ######### Sales #############
        try:
            self.m_n_num_sales = int(ptable1[2].find('td').text)
            #print('Sales :', self.m_n_num_sales)
        except Exception as e:
            print('Not Found: Sales', str(e))

            ######### Escrow ############
        try:
            self.m_s_escrow = ptable1[1].find('td').text
            #print('Escrow :', self.m_s_escrow)
        except Exception as e:
            print('Not Found: Escrow', str(e))

            ######### Views ############
        try:
            self.m_n_num_views = int(ptable1[3].find('td').text)
            #print('Views :', self.m_n_num_views)
        except Exception as e:
            print('Not Found: Views', str(e))

        # No info available for the following
        self.m_f_price_eur = -1
        self.m_s_category = ''
        self.m_f_price_bitcoin = -1
        self.m_s_quantity_in_stock = ''
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_s_already_sold = ''
        self.m_s_ads_post_date = ''
        self.m_s_vendor_email = ''

        # ########## Insert into Database ##########
        #self.insert_one_product_description()

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

            # ########## product title ##########
        try:
            self.m_s_product_title = aBeautifulSoup.findChild('span',{'class':'text-left h3'}).text[:255]
            print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

            # ####### Price ########
        try:
            ptable1 = aBeautifulSoup.findAll('table', {'class': 'table'})[0].find('tbody').findAll('tr')
            self.m_f_price_usd = float(ptable1[0].find('td').text.split('$')[0])
            self.m_s_min_amount_per_order = self.m_f_price_usd
            print('P1: ', self.m_f_price_usd)
            print('p2: ', self.m_s_min_amount_per_order)
        except Exception as e:
            print('Not Found: Price', str(e))

            # ########## Vendor Info ##########
        try:
            self.m_s_vendor_market_ID = aBeautifulSoup.find('a', {'class': 'font-weight-bold liberty'}).text
            self.m_s_vendor_market_name = self.m_s_vendor_market_ID
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                       self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('Vendor:', self.m_s_vendor_market_name)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))

            # Feedback Table
        i = 0
        reviewsCount = aBeautifulSoup.findAll('table', {'class': 'table'})[2].find('tbody').findAll('tr')
        if len(reviewsCount) == 0:
            print('No reviews yet')
        else:
            print('Review Count: ', len(reviewsCount)/2)
            while i < len(reviewsCount):
                # rating
                rating_stars = reviewsCount[i].find('th').text.strip()
                self.m_f_rating_stars = rating_stars
                print('rating: ', self.m_f_rating_stars)

                self.m_s_text_comments = reviewsCount[i].findAll('td')[1].text
                print('Comment: ', self.m_s_text_comments)

                self.m_s_post_date = reviewsCount[i].findAll('td')[3].text
                print('Review date: ', self.m_s_post_date)

                i = i + 2
                self.insert_one_product_rating()

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

            self.m_s_vendor_profile = aBeautifulSoup.find('pre', {'class': 'full-text'}).text
            print('Profile:', self.m_s_vendor_profile)

            vtable = aBeautifulSoup.find('div',{'class':'col-12 col-sm-3 col-xl-2 bg-white text-center p-1 mb-1 rounded'})

            # Extract Vendor Level
            self.m_n_vendor_level = vtable.findAll('p')[4].find('b').text
            print('Vendor Level', self.m_n_vendor_level)

            # Extract Orders completed
            self.m_n_num_orders_completed = vtable.findAll('p')[2].find('b').text
            print('Orders Completed', self.m_n_num_orders_completed)


            # Extract Average Rating
            self.m_f_avg_ratings = vtable.findAll('p')[3].find('b').text
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

        except Exception as e:
            print('Exception: ', str(e))
        try:
            reviewsTable = aBeautifulSoup.find('table', {'class': 'table text-left'}).find('tbody').findAll('tr')
            reviewcount = len(reviewsTable)
            print('Review count: ', reviewcount)
        except Exception as e:
            print(str(e))
        try:
            i = 0
            if(reviewcount == 0):
                print('No reviews')
            else:
                while i < len(reviewsTable):
                    self.m_s_text_comments = reviewsTable[i].findAll('td')[1].find('span').text
                    print('Comments:', self.m_s_text_comments)

                    self.m_f_rating_stars = len(reviewsTable[i].find('th').findAll('img'))
                    print('Rating:', self.m_f_rating_stars)

                    # Product title
                    self.m_s_product_title = reviewsTable[i+1].find('td').find('a').text.strip()
                    print('Product:', self.m_s_product_title)

                    # Date
                    self.m_s_post_date = reviewsTable[i].find('th').text
                    print('Date: ', self.m_s_post_date)

                    i = i + 2

                # Insert this rating to the db
                    self.insert_one_vendor_rating()

        except Exception as e:
            print('Not Found: Vendor Ratings.', str(e))
