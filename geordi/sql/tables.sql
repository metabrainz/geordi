BEGIN;

-- Schema 'geordi' should already exist.
CREATE TABLE geordi.csrf (ip text NOT NULL, csrf text NOT NULL);

CREATE TABLE geordi.editor (name text PRIMARY KEY, tz text, internal boolean not null default false);

CREATE TABLE geordi.item (id serial PRIMARY KEY, type text);
CREATE TABLE geordi.item_data (id text PRIMARY KEY, item integer not null REFERENCES item(id), data text);
CREATE TABLE geordi.item_redirect (old integer PRIMARY KEY, new integer REFERENCES item(id));
CREATE TABLE geordi.item_link (item integer not null REFERENCES item(id), linked integer not null REFERENCES item(id), type text not null);

CREATE TABLE geordi.raw_match (item integer NOT NULL REFERENCES item(id), editor text NOT NULL REFERENCES editor(name), type text not null, mbid text not null, timestamp TIMESTAMP WITH TIME ZONE not null, superseded boolean not null default false);

COMMIT;
