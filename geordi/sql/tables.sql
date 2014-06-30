BEGIN;

-- Schema 'geordi' should already exist, and it should be on the search path of the user this is run as.
CREATE TABLE geordi.csrf (ip text NOT NULL, csrf text NOT NULL, opts text, timestamp TIMESTAMP WITH TIME ZONE NOT NULL);

CREATE TABLE geordi.editor (name text PRIMARY KEY, tz text, internal boolean not null default false);

CREATE TABLE geordi.item (id serial PRIMARY KEY, type text, map text);
CREATE TABLE geordi.item_data (id text PRIMARY KEY, item integer not null REFERENCES item(id), data text);
CREATE TABLE geordi.item_redirect (old integer PRIMARY KEY, new integer REFERENCES item(id));
CREATE TABLE geordi.item_link (item integer not null REFERENCES item(id), linked integer not null REFERENCES item(id), type text not null);

CREATE TABLE geordi.entity (mbid text not null primary key, type text not null, data text);
CREATE TABLE geordi.raw_match (id serial PRIMARY KEY, item integer NOT NULL REFERENCES item(id), editor text NOT NULL REFERENCES editor(name), timestamp TIMESTAMP WITH TIME ZONE not null, superseded boolean not null default false);
CREATE TABLE geordi.raw_match_entity (raw_match integer NOT NULL references raw_match(id), entity text NOT NULL REFERENCES entity(mbid));

COMMIT;
