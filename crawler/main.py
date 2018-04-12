from PSStoreCrawler import PSStoreCrawler

crawler = PSStoreCrawler("https://store.playstation.com/", ['/es-es/grid/STORE-MSF75508-PLATFORMPS3','/es-es/grid/STORE-MSF75508-PS4CAT','/es-es/grid/STORE-MSF75508-PLATFORMPSVITA'],3)
crawler.crawl_psstore()