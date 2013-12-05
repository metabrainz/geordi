BEGIN;

-- Schema 'geordi' should already exist.
CREATE TABLE geordi.csrf (ip text NOT NULL, csrf text NOT NULL);

CREATE TABLE geordi.user (name text PRIMARY KEY, tz text);

CREATE TABLE geordi.item (id integer PRIMARY KEY, type text, map text, dirty boolean not null default false);
CREATE TABLE geordi.item_data (data_id text PRIMARY KEY, item_id integer PRIMARY KEY REFERENCES item(id));
CREATE TABLE geordi.item_redirect (old integer PRIMARY KEY, new integer REFERENCES item(id));
CREATE TABLE geordi.item_link (item integer not null REFERENCES item(id), linked integer not null REFERENCES item(id), type text not null);

CREATE TABLE geordi.raw_match (item integer NOT NULL REFERENCES item(id), user text NOT NULL REFERENCES user(name), type text not null, mbid text not null, timestamp TIMESTAMP WITH TIME ZONE not null, superseded boolean not null default false);

COMMIT;
