import scrapy

from letterboxd.items import ReviewItem


def stars_to_value(rating: str) -> int:  # turns ★★★★½ into 4.5
    value = 0
    for char in rating:
        if (char == '★'):
            value += 1
        elif (char == '½'):
            value += .5
    return int(value * 2)


class Review(scrapy.Spider):
    name = "reviews"

    base_url = "https://letterboxd.com"

    start_urls = [
        "https://letterboxd.com/members/popular/page/1/"
    ]

    # current_user = ""

    def reviews(self, response):
        user = response.css('h1.title-3 a::attr("href")').get()
        for film in response.css("li.poster-container"):
            movie_name = film.css(
                'li.poster-container div::attr("data-film-name")').get()
            movie_id = film.css(
                'li.poster-container div::attr("data-film-id")').get()
            year = film.css(
                'li.poster-container div::attr("data-film-release-year")').get()
            rating = film.css('span.rating::text').get()

            # if (not any([x is None for x in [movie_name, movie_id, rating]])):
            review = ReviewItem()
            review['user'] = user
            review['name'] = movie_name
            review['movie_id'] = movie_id
            review['year'] = year
            review['rating'] = stars_to_value(rating)
            yield review

            # else:
            #     print(user, movie_name, movie_id, year, rating)
            #     raise RuntimeError("field in data was None")

        # next_page = response.css('a.next::attr("href")').get()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.reviews)

    def parse(self, response):
        for user in response.css('table.person-table a.avatar::attr("href")').getall():
            # current_user = user
            request = scrapy.Request(
                self.base_url + "/" + user + "/films", callback=self.reviews)
            request.meta["user"] = user

            yield request

        # next_page = response.css('a.next::attr("href")').get()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)
