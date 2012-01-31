#!/usr/bin/perl -w

use strict;
use warnings;
use Getopt::Long;
use XML::XML2JSON;
use LWP::UserAgent;
use HTTP::Request;
use URI::Escape;
use Encode;

my $server = "127.0.0.1";
my $port = 9200;
my $index = "labelfeeds";
my $help = 0;

GetOptions(
    "port=i"        => \$port,
    "server=s"      => \$server,
    "index=s"       => \$index,
    "help|h"        => \$help,
) or exit(1);

if ($help) {
    print "Usage: submit.pl --port <port> --server <server> --index <index> [files]\n";
    exit(2);
}

local $/;
my $conv = XML::XML2JSON->new("content_key" => "text", "attribute_prefix" => "_");
my $ua = LWP::UserAgent->new;

binmode STDOUT, ":utf8";

foreach my $f (@ARGV) {
    my $base = $f;
    $base =~ s/(.*?)\/([^\/]+)$/$2/;
    my $url = sprintf("http://%s:%s/%s/product/%s", $server,
                                                    $port, 
                                                    uri_escape($index),
                                                    uri_escape($base));
    if (!-f $f)
    {
        print "Cannot find file $f. Skipping\n";
        next;
    }

    print "process $f\n";
    open(XML, $f) or die;
    binmode XML, ":utf8";
    my $xml = <XML>;
    close XML;

    my $json = $conv->convert($xml);
    my $req = HTTP::Request->new(PUT => $url);
    $req->content($json);
    $ua->request($req);

}
