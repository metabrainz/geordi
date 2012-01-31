use strict;
use warnings;

use DBI;
use JSON::Any;
use LWP::UserAgent;
use HTTP::Request;

my $dbh = DBI->connect('dbi:Pg:dbname=last;host=0.0.0.0;port=1234', 'lastfm', '')
    or die 'Could not connect';

my $sth = $dbh->prepare(
    'SELECT DISTINCT ON (album.id) album.id, *, recording.id AS recording
     FROM recording
     JOIN track ON recording.track = track.id
     JOIN album_track_join at ON at.track = track.id
     JOIN album ON album.id = at.album
     WHERE recording.source = 2 LIMIT 1000');
my $total = $sth->execute;

my %artist_cache;
my %label_cache;

binmode STDERR, ':utf8';

my $i = 1;
while (my $row = $sth->fetchrow_hashref) {
    my $document = {
        artist => get_artist($row->{artist}),
        label => do {
            my ($rl) = @{
                $dbh->selectrow_arrayref(
                    'SELECT label.name
                     FROM recording_label
                     JOIN label ON recording_label.label = label.id
                     WHERE recording = ?',
                    { Columns => [1] },
                    $row->{recording}
                ) || []
            };
            $rl;
        },
        title => $row->{title},
        release_date => $row->{releasedate},
        tracks => [
            map +{
                %$_,
                artist => get_artist($row->{artist}),
            }, @{
                $dbh->selectall_arrayref(
                    'SELECT track.date, track.title, at.position, recording.duration,
                       track.id
                     FROM recording
                     JOIN track ON track.id = recording.track
                     JOIN artist ON track.artist = artist.id
                     JOIN album_track_join at ON at.track = track.id
                     WHERE at.album = ?',
                    { Slice => {} }, $row->{id})
            }
        ]
    };
#    if(fork() == 0) {
        my $lwp = LWP::UserAgent->new;
        my $req = HTTP::Request->new( PUT => 'http://0.0.0.0:9200/lastfm/release/mm-' . $row->{album} );
        $req->content(JSON::Any->new( utf8 => 1 )->objToJson($document));
        $lwp->request($req);
#        exit(0);
#    }

    print STDERR $i++ . " / $total\r";
}

sub get_artist {
    my $id = shift or return undef;
    $artist_cache{$id} ||= do {
        my $artist = $dbh->selectrow_hashref('SELECT name FROM artist WHERE id = ?', {}, $id);
        $artist && $artist->{name}
    };
    return $artist_cache{$id};
}
