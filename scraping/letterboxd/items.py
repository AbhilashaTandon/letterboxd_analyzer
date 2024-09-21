# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ReviewItem(Item):
    user = Field()
    name = Field()
    movie_id = Field()
    rating = Field()
