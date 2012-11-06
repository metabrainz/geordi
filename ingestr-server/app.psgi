use strict;
use warnings;

use Encode;
use JSON::Any;
use LWP::UserAgent;
use Plack::Request;
use Plack::Response;
use Text::Xslate;
use List::UtilsBy qw( sort_by );
use Sort::Naturally qw( ncmp );

sub extract_acoustid
{
   my $block = shift;
   my $acoustid = use_first_text($block, qr{acoustid});
   $acoustid =~ s/urn:acoustid://;
   return $acoustid unless $acoustid eq 'unknown';
}

sub use_first_text
{
   my ($block, $regex) = @_;
   $regex //= qr{.*};
   if (ref($block) eq 'ARRAY') {
       my @items = grep { $_->{text} =~ $regex } @{ $block };
       return $items[0]->{text};
   } else {
       return defined $block ? $block->{text} : $block;
   }
}

sub all_but_first_text
{
   my ($block, $regex) = @_;
   $regex //= qr{.*};
   if (ref($block) eq 'ARRAY') {
       my @items = grep { $_->{text} =~ $regex } @{ $block };
       return [map { $_->{text} } @items[1..scalar @items - 1]];
   } else {
       return undef;
   }
}

my $processors = {
    wcd => sub {
        my $input_json = shift;
        my @acceptable_formats = ('flac', 'vbr mp3', 'apple lossless audio', 'ogg vorbis');
        my $track_count = scalar grep { my $form = $_->{format}{text}; $_->{"_source"} eq "original" && grep { lc($form) eq $_ } @acceptable_formats } @{ $input_json->{"_source"}{"files.xml"}{files}{file} };
        my $tracks = [ sort { ncmp($a->{number}, $b->{number}) }
                       map +{ number => $_->{track}{text},
                              length => $_->{length}{text},
                              artist => $_->{artist}{text},
                              title => $_->{title}{text},
                              acoustid => extract_acoustid($_->{"external-identifier"})
                            }, grep { my $form = $_->{format}{text}; $_->{"_source"} eq "original" && grep { lc($form) eq $_ } @acceptable_formats } @{ $input_json->{"_source"}{"files.xml"}{files}{file} } ];
        return {
                 release_title => use_first_text($input_json->{"_source"}{"meta.xml"}{metadata}{album}) // $input_json->{"_source"}{"meta.xml"}{metadata}{title}{text} =~ s, / .*$,,r,
                 alternate_release_titles => all_but_first_text($input_json->{"_source"}{"meta.xml"}{metadata}{album}),
                 release_date => $input_json->{"_source"}{"meta.xml"}{metadata}{year}{text},
                 release_artist => $input_json->{"_source"}{"meta.xml"}{metadata}{artist}{text} // $input_json->{"_source"}{"meta.xml"}{metadata}{creator}{text},
                 track_count => $track_count,
                 print_acoustid => 1,
                 tracks => $tracks
               }
    }
};

my $json = JSON::Any->new( pretty => 1, utf8 => 1 );
my $tx = Text::Xslate->new(
    function => {
        json => sub { decode('utf-8', $json->objToJson(shift)) }
    }
);
my $ua = LWP::UserAgent->new;

my $app = sub {
    my ($env) = @_;
    my $req = Plack::Request->new($env);

    my $res;
    if (my ($index, $identifier) = $req->path =~ /^\/([^\/]+)\/([^\/]+)$/) {
        my $search_res = $ua->get('http://0.0.0.0:9200/' . $index . '/item/' . $identifier);
        my $doc = $json->jsonToObj($search_res->decoded_content);
        use Devel::Dwarn; Dwarn $search_res;
        $res = Plack::Response->new(
            200, [],
            encode('utf8',$tx->render('document.tx', { document => $doc }))
        );
    }
    else {
        if (my $search = $req->param('query')) {
            my $search_res = $ua->get('http://0.0.0.0:9200/_search?q=' . $search);
            my $results = $json->jsonToObj($search_res->decoded_content);
            for my $result (@{ $results->{hits}->{hits} }) {
                my $res_copy = $result;
                $result->{"_ingestr"} = $processors->{$result->{_index}}($res_copy);
            }
            my $body = $tx->render('results.tx', {
                results => $results->{hits},
            });
            $res = Plack::Response->new(200,
                                        [
                                            'Content-Type' => 'text/html;charset=UTF-8'
                                        ],
                                        encode('utf8', $body));
        } else {
            $res = Plack::Response->new(
                200, [],
                $tx->render('index.tx', {  })
            );
        }
    }

    return $res->finalize;
};

$app;
