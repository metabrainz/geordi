use strict;
use warnings;

use Encode;
use JSON::Any;
use LWP::UserAgent;
use Plack::Request;
use Plack::Response;
use Text::Xslate;

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
    if (my ($file) = $req->path =~ /^\/(.+)$/) {
        my $search_res = $ua->get('http://0.0.0.0:9200/umg/product/' . $file);
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
