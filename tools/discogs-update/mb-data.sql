SELECT 'artist'::text, regexp_replace(url.url, '^http://www.discogs.com/artist/', ''), string_agg(artist.gid::text, ',')
  FROM url
  JOIN l_artist_url ON url.id = l_artist_url.entity1
  JOIN artist ON l_artist_url.entity0 = artist.id
 WHERE url.url ~ '^http://www.discogs.com/artist/'
 GROUP BY regexp_replace(url.url, '^http://www.discogs.com/artist/', '')
UNION
SELECT 'release'::text, regexp_replace(url.url, '^http://www.discogs.com/release/', ''), string_agg(release.gid::text, ',')
  FROM url
  JOIN l_release_url ON url.id = l_release_url.entity1
  JOIN release ON l_release_url.entity0 = release.id
 WHERE url.url ~ '^http://www.discogs.com/release/'
 GROUP BY regexp_replace(url.url, '^http://www.discogs.com/release/', '')
UNION
SELECT 'master'::text, regexp_replace(url.url, '^http://www.discogs.com/master/', ''), string_agg(release_group.gid::text, ',')
  FROM url
  JOIN l_release_group_url ON url.id = l_release_group_url.entity1
  JOIN release_group ON l_release_group_url.entity0 = release_group.id
 WHERE url.url ~ '^http://www.discogs.com/release_group/'
 GROUP BY regexp_replace(url.url, '^http://www.discogs.com/master/', '')
UNION
SELECT 'label'::text, regexp_replace(url.url, '^http://www.discogs.com/label/', ''), string_agg(label.gid::text, ',')
  FROM url
  JOIN l_label_url ON url.id = l_label_url.entity1
  JOIN label ON l_label_url.entity0 = label.id
 WHERE url.url ~ '^http://www.discogs.com/label/'
 GROUP BY regexp_replace(url.url, '^http://www.discogs.com/label/', '');
