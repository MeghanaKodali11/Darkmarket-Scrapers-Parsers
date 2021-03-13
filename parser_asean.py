import os
from bs4 import BeautifulSoup
from parser_base import parser_base


class parser_asean(parser_base):
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
            self.m_s_product_title = aBeautifulSoup.findChild('div',
                                                              {'class': 'breadcrumbs'}).findChild('h4').text[:255]
            print('PT: ', self.m_s_product_title)
        except Exception as e:
            print('Not Found: Product Title', str(e))

        # ########## Category ##########
        try:
            self.m_s_category = \
                aBeautifulSoup.findAll('a', {'class': 'btn btn-sm btn-link btn-no-margin custom-link-action'})[1].text
            #print('PC: ', self.m_s_category)
        except Exception as e:
            print('Not Found: Category', str(e))

        # ########## Price ##########
        try:
            priceText = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('td')[0].text
            priceTextUsd = priceText.split('USD')[0]
            self.m_f_price_usd = float(priceTextUsd)
            self.m_s_min_amount_per_order = priceTextUsd.strip()
            #print('P1: ', self.m_f_price_usd)
            #print('p2: ', self.m_s_min_amount_per_order)
        except Exception as e:
            print('Not Found: Price', str(e))

        # ########## Vendor Info ##########
        try:
            vendorIdHref = aBeautifulSoup.findAll('a', {'class': 'btn btn-sm btn-link btn-no-margin custom-link-action'})[0][
                    'href']

            self.m_s_vendor_market_ID = vendorIdHref[vendorIdHref.rindex('/') + 1:]

            self.m_s_vendor_market_name = \
                aBeautifulSoup.findAll('a', {'class': 'btn btn-sm btn-link btn-no-margin custom-link-action'})[
                    0].text.strip()
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            #print('VID: ', self.m_n_vendor_global_ID)
        except Exception as e:
            print('Not Found: Vendor Info', str(e))

        # ########## Product Description ##########
        try:
            self.m_s_product_desc = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('td')[8].text

            #print(self.m_s_product_desc)
            # Check for other product description files and append.
        except Exception as e:
            print('Not Found: Product Description', str(e))

            ########## Ships from ##############
        try:
            self.m_s_ships_from = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('td')[6].text
            #print('Ships from', self.m_s_ships_from)
        except Exception as e:
            print('Not Found: Ships from', str(e))

            ########## Ships to ##############
        try:
            self.m_s_ships_from = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('td')[7].text
            #print('Ships to', self.m_s_ships_from)
        except Exception as e:
            print('Not Found: Ships from', str(e))

        # No info available for the following
        self.m_s_escrow = ''
        self.m_n_num_stock = '0'
        self.m_n_num_sales = '0'
        self.m_f_price_eur = -1
        self.m_f_price_bitcoin = -1
        self.m_s_quantity_in_stock = ''
        self.m_s_min_amount_per_order = ''
        self.m_s_max_amount_per_order = ''
        self.m_s_already_sold = ''
        self.m_n_num_views = 0
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

            self.m_s_product_title = aBeautifulSoup.findChild('div', {'class': 'breadcrumbs'}).findChild('h4').text
            print('PT: ', self.m_s_product_title)

            # ########## Price ##########

            priceText = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('td')[
                0].text.split('USD')[0]
            self.m_f_price_usd = float(priceText)
            print('PC: ', self.m_f_price_usd)

            ########## Vendor Info ##########

            vendorIdHref = aBeautifulSoup.findAll('a', {'class': 'btn btn-sm btn-link btn-no-margin custom-link-action'})[0]['href']
            print(vendorIdHref)
            self.m_s_vendor_market_ID = vendorIdHref[vendorIdHref.rindex('/') + 1:]
            print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = \
                aBeautifulSoup.findAll('a', {'class': 'btn btn-sm btn-link btn-no-margin custom-link-action'})[
                    0].text.strip()
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            print('VID: ', self.m_n_vendor_global_ID)
            print('VN:', self.m_s_vendor_market_name)

            # Feedback Table
            reviewsTable = aBeautifulSoup.find('table', {'class': 'table table-compact table-no-margin'})
            if reviewsTable:
                #print('Table Present')
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
                        if self.m_f_rating_stars == "Positive":
                            self.m_f_rating_stars = "5"
                        elif self.m_f_rating_stars == "Negative":
                            self.m_f_rating_stars = "0"
                        else:
                            self.m_f_rating_stars = "2"

                        self.m_s_text_comments = reviewRow.findAll('td')[2].text
                        print('Comment: ', self.m_s_text_comments)
                        self.insert_one_product_rating()
                else:
                    print('No Reviews Yet.')

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
            #print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('tr')[0].find(
                'td').text.strip()
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,self.m_s_vendor_market_ID)
            #print('VID: ', self.m_n_vendor_global_ID)
            #print('VN:', self.m_s_vendor_market_name)

            self.m_s_vendor_profile = aBeautifulSoup.find('div', {'class': 'white-space-formatted'}).text
            #print('Profile:', self.m_s_vendor_profile)

            # Extract join date
            aVendorInfo1 = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1]

            self.m_s_join_date_member_since = aVendorInfo1.findAll('tr')[2].find('td').text.strip()
            #print(self.m_s_join_date_member_since)

            # Extract No. of ratings
            aVendorRatings = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('tr')[4].find(
                'td')
            self.m_n_num_ratings = int(aVendorRatings.findAll('a')[0].find('span').text.strip())
            self.m_n_num_ratings_positive = int(aVendorRatings.findAll('a')[1].find('span').text.strip())
            self.m_n_num_ratings_negative = int(aVendorRatings.findAll('a')[2].find('span').text.strip())
            print(self.m_n_num_ratings, self.m_n_num_ratings_positive, self.m_n_num_ratings_negative)

            # No info available for the following
            self.m_n_num_ratings_neutral = '0'
            self.m_s_terms_conditions = ''
            self.m_s_last_active_date = ''
            self.m_n_num_orders_open = -1
            self.m_s_pgp = ''
            self.m_f_total_revenue = -1
            self.m_n_trust_level = -1
            self.m_n_trust_seller_yes_or_no = -1  # 0 no; 1 yes; -1, missing
            self.m_n_num_trust_yes = -1
            self.m_n_num_trust_no = -1
            self.m_f_avg_ratings = -1
            self.m_s_fe_enabled = ''
            self.m_n_vendor_level = '0'
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
            #print(self.m_s_vendor_market_ID)
            self.m_s_vendor_market_name = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('tr')[0].find(
                'td').text.strip()
            self.m_n_vendor_global_ID = self.query_vendor_list_by_vendor_market_ID(self.m_n_cryptomarket_global_ID,
                                                                                   self.m_s_vendor_market_ID)
            #print('VID: ', self.m_n_vendor_global_ID)
            #print('VN:', self.m_s_vendor_market_name)

            aVendorRatings = aBeautifulSoup.findAll('table', {
                'class': 'table table-vertical table-noborder table-compact table-no-margin'})[1].findAll('tr')[4].find(
                'td')
            self.m_n_num_ratings = int(aVendorRatings.findAll('a')[0].find('span').text.strip())

            print('Review Count: ', int(self.m_n_num_ratings))

            reviewsTable = aBeautifulSoup.find('table', {'class': 'table table-compact table-no-margin'}).find(
                'tbody').findAll('tr')
            if self.m_n_num_ratings > 0:
                for reviewRow in reviewsTable:
                    if reviewRow.findAll('td')[2].find('span').text == "Positive" or reviewRow.findAll('td')[2].find(
                            'span').text == "Negative":
                        # Review Comments
                        self.m_s_text_comments = reviewRow.findAll('td')[3].text.strip()
                        #print('Comments:', self.m_s_text_comments)
                        # Product title
                        self.m_s_product_title = reviewRow.findAll('td')[1].find('a').text.strip()
                        #print('Product:', self.m_s_product_title)

                        # Date
                        self.m_s_post_date = reviewRow.findAll('td')[4].text.strip()
                        #print('Date: ', self.m_s_post_date)

                        # Insert this rating to the db
                        self.insert_one_vendor_rating()
        except Exception as e:
            print('Not Found: Vendor Ratings.', str(e))