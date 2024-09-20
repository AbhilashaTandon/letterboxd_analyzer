import scrapy

class ReviewSpider(scrapy.Spider):
    name = "reviews"
    start_urls = ['https://letterboxd.com/members/popular/this/all-time/page/']

    def parse(self, response):
        for user in response.css("a.avatar"):
            yield {
                "href": user.css()
            }