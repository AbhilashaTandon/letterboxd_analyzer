from pathlib import Path

import scrapy


def stars_to_value(rating: str) -> int:  # turns ★★★★½ into 4.5
    value = 0
    for char in rating:
        if (char == '★'):
            value += 1
        elif (char == '½'):
            value += .5
    return int(value * 2)


class UserSpider(scrapy.Spider):
    name = "user"

    start_urls = [
        "https://letterboxd.com/members/popular/page/1/"
    ]

    def reviews(self, response):
        for film in response.css("li.poster-container"):
            yield {
                "user": film.css('h1.title3 a::attr("href")'),
                "name": film.css('div.poster::attr("data-film-name")'),
                "year": film.css('div.poster::attr("data-film-release-year")'),
                "id":   film.css('div.poster::attr("data-film-id")'),
                "rating": stars_to_value(film.css('span.rating::text')),
            }

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.reviews)

    def parse(self, response):
        for user in response.css('table.person-table a.avatar::attr("href")').getall():
            user_films = response.follow(user + "films", callback=self.reviews)
            yield {
                "user": user,
                "reviews": user_films
            }

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

# to run this run
