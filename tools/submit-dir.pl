#!/usr/bin/perl -w

use strict;
use warnings;
use Getopt::Long;
use XML::XML2JSON;
use LWP::UserAgent;
use HTTP::Request;
use URI::Escape;
use Encode;
use JSON;
use Try::Tiny;

use File::Slurp qw( read_file read_dir );

my $server = "127.0.0.1";
my $port = 9200;
my $index;
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

unless ($index) {
    print "Must supply an index name\n";
    exit(2);
}

my $conv = XML::XML2JSON->new("content_key" => "text", "attribute_prefix" => "_");
my $ua = LWP::UserAgent->new;

binmode STDOUT, ":utf8";

foreach my $dir (@ARGV) {
    my $base = $dir;
    $base =~ s/(.*?)\/([^\/]+)\/?$/$2/;
    my $url = sprintf("http://%s:%s/%s/item/%s", $server,
                                                 $port,
                                                 uri_escape($index),
                                                 uri_escape($base));
    if (!-d $dir)
    {
        print "Cannot find directory $dir. Skipping...\n";
        next;
    }

    print "process $dir\n";
    my %json;

    foreach my $file (read_dir($dir)) {
        my $filebase = $file;
        # Trim out repetition of the identifier
        $filebase =~ s/$base//;
        # Trim leading/trailing separators
        $filebase =~ s/^[\s_-]+|[\s_-]+$//;
        # Replace periods with underscores
        $filebase =~ s/\./_/g;

        my $filecontent = read_file("$dir/$file");
        if ($file =~ /\.xml$/) {
            my $xml_to_json = $conv->convert($filecontent);
            $json{$filebase} = decode_json($xml_to_json);
        } elsif ($file =~ /\.json$/) {
            try {
                $json{$filebase} = decode_json($filecontent);
            } catch {
                print "JSON file $file threw an error, skipping.\n";
                next;
            }
        } else {
            $json{$filebase} = $filecontent;
        }
    }
    my $req = HTTP::Request->new(PUT => $url);

    $req->content(encode_json(\%json));
    $ua->request($req);

}
