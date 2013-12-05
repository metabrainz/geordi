BEGIN;

CREATE TABLE csrf (ip text NOT NULL, csrf text NOT NULL);
CREATE TABLE user (name text PRIMARY KEY, tz text);
CREATE TABLE item (id integer PRIMARY KEY, type text, map text);
CREATE TABLE item_data (data_id text PRIMARY KEY, item_id integer PRIMARY KEY REFERENCES item(id));
CREATE TABLE item_redirect (old integer PRIMARY KEY, new integer REFERENCES item(id));
CREATE TABLE match (item integer NOT NULL REFERENCES item(id), user text NOT NULL REFERENCES user(name), type text not null, mbid text not null, timestamp TIMESTAMP WITH TIME ZONE not null);
CREATE TABLE item_link (item integer not null REFERENCES item(id), linked integer not null REFERENCES item(id), type text not null);

COMMIT;
