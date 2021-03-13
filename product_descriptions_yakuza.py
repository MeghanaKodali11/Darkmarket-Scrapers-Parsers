# You need to update three places for a new Market!
from parser_base import parser_base
from parser_yakuza import parser_yakuza  # You need to update this (Place 1) for a new Market!

# The main function, the entry point
if __name__ == '__main__':
    aParserBase = parser_base()
    aParserBase.m_n_cryptomarket_global_ID = 46  # You need to update this (Place 2) for a new Market!
    aParserBase.select_last_parsed_scraping_event_IDs()

    # parse product descriptions from the "product_desc_scraping_event" table
    n_last_parsed_scraping_event_ID_pd = aParserBase.m_n_last_parsed_scraping_event_ID_pd
    vaProductDescScrapingEvents = aParserBase.select_product_desc_scraping_event(n_last_parsed_scraping_event_ID_pd)
    nNumOfScrapingEvents = len(vaProductDescScrapingEvents)
    nIndexOfProgress = 0
    for aProductDescScrapingEvent in vaProductDescScrapingEvents:
        print('%d / %d' % (nIndexOfProgress, nNumOfScrapingEvents))
        nIndexOfProgress += 1
        aOneParser = parser_yakuza()  # You need to update this (Place 3) for a new Market!
        n_scraping_event_ID_pd = aProductDescScrapingEvent['scraping_event_ID_product']
        n_product_global_ID = aProductDescScrapingEvent['product_global_ID']
        s_scraping_time = aProductDescScrapingEvent['scraping_time']
        s_product_desc_file_path = aProductDescScrapingEvent['product_desc_file_path_in_FS']
        [n_cryptomarket_global_ID, s_product_market_ID] = aParserBase.query_product_list_by_product_global_ID(n_product_global_ID)
        # we need to parse the product desc page for product descriptions
        aOneParser.m_n_cryptomarket_global_ID = n_cryptomarket_global_ID
        aOneParser.m_n_product_global_ID = n_product_global_ID
        aOneParser.m_s_product_market_ID = s_product_market_ID
        aOneParser.m_s_scraping_time = s_scraping_time
        aOneParser.select_root_directories_of_one_market()
        aOneParser.m_s_html_file_name_pd = aOneParser.m_sRemoteRootDirectoryProductDesc + s_product_desc_file_path
        aOneParser.m_s_local_file_name_pd = aOneParser.m_s_local_directory + s_product_desc_file_path
        aOneParser.parse_one_html_product_descriptions()
        # update the scraping_event_ID frequently, the program can stop at any time.
        aParserBase.m_n_last_parsed_scraping_event_ID_pd = n_scraping_event_ID_pd
        aParserBase.update_last_parsed_scraping_event_ID_pd()