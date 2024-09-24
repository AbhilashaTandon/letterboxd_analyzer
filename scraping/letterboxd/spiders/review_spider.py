import scrapy

from letterboxd.items import ReviewItem


def stars_to_value(rating: str) -> int:  # turns ★★★★½ into 9
    value = 0
    for char in rating:
        if (char == '★'):
            value += 2
        elif (char == '½'):
            value += 1
    return value


class Review(scrapy.Spider):
    name = "reviews"

    base_url = "https://letterboxd.com"

    start_urls = [
        "https://letterboxd.com/members/popular/page/80/"
    ]

    # current_user = ""

    def reviews(self, response):
        user = response.css('h1.title-3 a::attr("href")').get()
        for film in response.css("li.poster-container"):
            movie_name = film.css(
                'div::attr("data-film-slug")').get()
            movie_id = film.css(
                'div::attr("data-film-id")').get()
            rating = film.css('span.rating::text').get()

            if (rating is None):
                continue
            if (movie_name is None):
                continue
            if (movie_id is None):
                continue

            review = ReviewItem()
            review['user'] = user
            review['name'] = movie_name
            review['movie_id'] = movie_id
            review['rating'] = stars_to_value(rating)
            yield review

            # else:
            #     print(user, movie_name, movie_id, year, rating)
            #     raise RuntimeError("field in data was None")

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.reviews)

    def parse(self, response):
        for user in response.css('table.person-table a.avatar::attr("href")').getall():
            # current_user = user
            request = scrapy.Request(
                self.base_url + user + "films", callback=self.reviews)
            request.meta["user"] = user

            yield request

        next_page = response.css('a.next::attr("href")').get()

        with open("../log.txt", mode='a') as log_file:
            log_file.write("currently getting users from page %s" % next_page)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


# i last stopped at {'movie_id': '341754', 'name': 'detroit', 'rating': 6, 'user': '/alexhurding/'}
