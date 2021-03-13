import os
import logging
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def selenium_setup_firefox_network():
    # Setup Firefox browser for visiting .onion sites through Tor
    # If you are using a computer (the local Ubuntu OS) on the campus network,
    # (which cannot access the Tor network but can access the Jaguar db server),
    # you need to first enable VPN on the local Ubuntu OS. Please use the marshmallow server as the VPN.
    # If you are using a computer on the EBCS network,
    # (which can access both the Tor network and the Jaguar db server),
    # you can directly start from this line.
    # In both cases, you need to make sure that the Tor client is running on the local Ubuntu OS.
    # To ensure that, you can run the following command in the Ubuntu Terminal:
    # sudo systemctl restart tor
    # sudo systemctl start tor
    LOGGER.setLevel(logging.ERROR)  # to remove geckodriver.log
    aProfile = webdriver.FirefoxProfile()  # open firefox, enter "about:config"
    aProfile.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = True  # manual javascript disabled its needed for genesis market
    aProfile.set_preference("network.proxy.type", 1)  # Manual proxy configuration
    aProfile.set_preference("network.proxy.socks", "127.0.0.1")  # SOCKS Host # local proxy
    aProfile.set_preference("network.proxy.socks_port", 9050)  # You can use any port, make sure it is consistent with the port used in the above SSH command.
    aProfile.set_preference("network.proxy.socks_remote_dns", True)  # Proxy DNS when using SOCKS v5
    aProfile.set_preference("network.dns.blockDotOnion", False)  # do not block .onion domains
    aProfile.set_preference("browser.download.folderList", 2) # for changing the download folder
    aProfile.set_preference("browser.download.manager.showWhenStarting", False)
    aProfile.set_preference("browser.download.dir", "/home/rob/temp_scrapedhtml/")


    aBrowserDriver = webdriver.Firefox(aProfile, executable_path='/home/rob/geckodriver/geckodriver', log_path=os.devnull)
    aBrowserDriver.set_page_load_timeout(30000)


    return aBrowserDriver
