SELECT movie_count.movie_id, movie_count.name, movie_count.count_, reviews.user_id, reviews.rating
FROM (
    SELECT reviews.movie_id, movies.name, 
    COUNT(reviews.movie_id) as count_
    FROM reviews JOIN movies ON movies.id = movie_id 
    GROUP BY reviews.movie_id, movies.name, reviews.user_id 
    ORDER BY Count(reviews.movie_id) DESC LIMIT 6000
) 
movie_count JOIN reviews ON reviews.movie_id = movie_count.movie_id
ORDER BY movie_count.count_ DESC;