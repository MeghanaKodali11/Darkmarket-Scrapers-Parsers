# You need to update three places for a new Market!
from parser_base import parser_base
from parser_liberty import parser_liberty # You need to update this (Place 1) for a new Market!

# The main function, the entry point
if __name__ == '__main__':
    aParserBase = parser_base()
    aParserBase.m_n_cryptomarket_global_ID = 58 # You need to update this (Place 2) for a new Market!
    aParserBase.select_last_parsed_scraping_event_IDs()

    # parse vendor ratings from the "vendor_rating_scraping_event" table
    n_last_parsed_scraping_event_ID_vr = aParserBase.m_n_last_parsed_scraping_event_ID_vr
    vaVendorRatingScrapingEvents = aParserBase.select_vendor_rating_scraping_event(n_last_parsed_scraping_event_ID_vr)
    nNumOfScrapingEvents = len(vaVendorRatingScrapingEvents)
    nIndexOfProgress = 0
    for aVendorRatingScrapingEvent in vaVendorRatingScrapingEvents:
        print('%d / %d' % (nIndexOfProgress, nNumOfScrapingEvents))
        nIndexOfProgress += 1
        aOneParser = parser_liberty() # You need to update this (Place 3) for a new Market!
        n_scraping_event_ID_vr = aVendorRatingScrapingEvent['scraping_event_ID_vendor']
        n_vendor_global_ID = aVendorRatingScrapingEvent['vendor_global_ID']
        s_scraping_time = aVendorRatingScrapingEvent['scraping_time']
        s_vendor_rating_file_path = aVendorRatingScrapingEvent['vendor_rating_file_path_in_FS']
        [n_cryptomarket_global_ID, s_vendor_market_ID] = aParserBase.query_vendor_list_by_vendor_global_ID(n_vendor_global_ID)
        # we need to parse the vendor rating page for vendor ratings
        aOneParser.m_n_cryptomarket_global_ID = n_cryptomarket_global_ID
        aOneParser.m_n_vendor_global_ID = n_vendor_global_ID
        aOneParser.m_s_vendor_market_ID = s_vendor_market_ID
        aOneParser.m_s_scraping_time = s_scraping_time
        aOneParser.select_root_directories_of_one_market()
        aOneParser.m_s_html_file_name_vr = aOneParser.m_sRemoteRootDirectoryVendorRating + s_vendor_rating_file_path
        aOneParser.m_s_local_file_name_vr = aOneParser.m_s_local_directory + s_vendor_rating_file_path
        aOneParser.parse_one_html_vendor_ratings()
        # update the scraping_event_ID frequently, the program can stop at any time.
        aParserBase.m_n_last_parsed_scraping_event_ID_vr = n_scraping_event_ID_vr
        aParserBase.update_last_parsed_scraping_event_ID_vr()

    print('job is done!')
