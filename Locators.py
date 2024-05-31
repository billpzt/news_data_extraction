class Locators():
    search_button_xpath = "//button[contains(@data-element, 'search-button')]"
    searchbar_xpath = "//input[contains(@name, 'q')]"
    dropdown_xpath = "//select[contains(@name, 's')]"
    next_results_xpath = '//div[@class="search-results-module-next-page"]'
    
    articles_xpath = '//ul[@class="search-results-module-results-menu"]/li'
    
    article_title_xpath = '//div/h3[@class="promo-title"]'
    article_description_xpath = './/p[@class="promo-description"]'
    article_date_xpath = '//p[@class="promo-timestamp"]'
    article_image_xpath = '//img[@class="image"]'
