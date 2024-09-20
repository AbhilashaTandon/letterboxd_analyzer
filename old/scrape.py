from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
import time

driver = webdriver.Chrome(ChromeDriverManager().install())

search_queries = ["best+movies", "my+favorites",
                  "favorite+films", "best+films", "my+top+pics", "must+watch", "my+top+movies", "my+favorite+movies", "my+best+movies", "my+must+watch+movies", "amazing+movies", "movies+i+like", "movies+i+love"]

DOMAIN = "https://letterboxd.com/search/lists/"

for query in search_queries:
    driver.get(DOMAIN + query)

    show_more_results = driver.find_elements_by_class_name(
        'load-more-search')

    while len(show_more_results) > 0:
        button = show_more_results[0]

        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')

        time.sleep(3)

        ActionChains(driver).move_to_element(
            button)

        time.sleep(1)

        ActionChains(driver).click(button).perform()

        time.sleep(3)

        temp_lists = [list_.get_attribute(
            'href') for list_ in driver.find_elements_by_class_name('list-link')]

        if (len(temp_lists) == 0):  # we clicked the wrong thing and there are no lists on the page
            break

        lists = temp_lists

        show_more_results = driver.find_elements_by_class_name(
            'load-more-search')

    lists = [list_.get_attribute(
        'href') for list_ in driver.find_elements_by_class_name('list-link')]

    with open('Dev/Programming/python/letterboxd_analyzer/lists.txt', mode='a', encoding='utf-8') as file:
        for list_ in lists:
            file.write(str(list_) + '\n')  # write link to list to file

    print(len(lists))

    driver.close()
