#!/bin/bash
set -e


function usage {
    cat <<HELP_USAGE
    usage: $0 [-hd] [-s bucket]
    -d --develop           Run Hugo in interactive development mode
                           (asciidoc images will show broken)
    -s --sync bucket/path  S3 bucket name to sync generate content and
                           optionally starting path (e.g, bucket/docs)
    -h --help              display help
HELP_USAGE
}


while [ "$1" != "" ]; do
    case $1 in
        -d | --develop )        docker run --rm -p 1313:1313 -v $PWD/hugo:/hugo-project gadams999/hugo-ubuntu:latest
                                exit
                                ;;
        -s | --sync )           shift
                                bucket=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

# For all processes, clear out previous content, build, and validate

# Clean out public folder completely (but don't delete folder)
shopt -s dotglob
rm -rf hugo/public/*
shopt -u dotglob

# Generate content
docker run --rm -p 1313:1313 -v $PWD/hugo:/hugo-project gadams999/hugo-ubuntu:latest hugo

# Test HTML links
htmltest -c .htmltest.yml hugo/public

# If bucket name was provided, clear existing bucket and upload latest build

if ! [ -z ${bucket+x} ]
then
    echo Syncing content to S3 bucket: $bucket
    aws s3 rm s3://$bucket --recursive
    aws s3 sync hugo/public s3://$bucket
fi