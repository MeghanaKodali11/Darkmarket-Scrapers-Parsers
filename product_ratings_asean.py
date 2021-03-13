from parser_base import parser_base
from parser_asean import parser_asean

# The main function, the entry point
if __name__ == '__main__':
    aParserBase = parser_base()
    aParserBase.m_n_cryptomarket_global_ID = 41  # You need to update this (Place 2) for a new Market!
    aParserBase.select_last_parsed_scraping_event_IDs()

    # parse product ratings from the "product_desc_scraping_event" table
    n_last_parsed_scraping_event_ID_pr = aParserBase.m_n_last_parsed_scraping_event_ID_pr
    vaProductRatingScrapingEvents = aParserBase.select_product_rating_scraping_event(n_last_parsed_scraping_event_ID_pr)
    nNumOfScrapingEvents = len(vaProductRatingScrapingEvents)
    nIndexOfProgress = 0

    for aProductRatingScrapingEvent in vaProductRatingScrapingEvents:
        print('%d / %d' % (nIndexOfProgress, nNumOfScrapingEvents))
        nIndexOfProgress += 1
        aOneParser = parser_asean()
        n_scraping_event_ID_pr = aProductRatingScrapingEvent['scraping_event_ID_product']
        n_product_global_ID = aProductRatingScrapingEvent['product_global_ID']
        s_scraping_time = aProductRatingScrapingEvent['scraping_time']
        s_product_rating_file_path = aProductRatingScrapingEvent['product_rating_file_path_in_FS']
        [n_cryptomarket_global_ID, s_product_market_ID] = aParserBase.query_product_list_by_product_global_ID(n_product_global_ID)
        # we need to parse the vendor rating page for vendor ratings
        aOneParser.m_n_cryptomarket_global_ID = n_cryptomarket_global_ID
        aOneParser.m_n_product_global_ID = n_product_global_ID
        aOneParser.m_s_product_market_ID = s_product_market_ID
        aOneParser.m_s_scraping_time = s_scraping_time
        aOneParser.select_root_directories_of_one_market()
        aOneParser.m_s_html_file_name_pr = aOneParser.m_sRemoteRootDirectoryProductRating + s_product_rating_file_path
        aOneParser.m_s_local_file_name_pr = aOneParser.m_s_local_directory + s_product_rating_file_path
        aOneParser.parse_one_html_product_ratings()
        # update the scraping_event_ID frequently, the program can stop at any time.
        aParserBase.m_n_last_parsed_scraping_event_ID_pr = n_scraping_event_ID_pr
        aParserBase.update_last_parsed_scraping_event_ID_pr()
    print('job is done!')
