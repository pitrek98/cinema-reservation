CREATE KEYSPACE IF NOT EXISTS cinema
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 2
};

USE cinema;

CREATE TABLE IF NOT EXISTS seats (
    movie_id text,
    seat_id text,
    reserved boolean,
    reserved_by text,
    reservation_time timestamp,
    PRIMARY KEY (movie_id, seat_id)
);