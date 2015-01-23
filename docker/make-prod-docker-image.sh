#!/bin/sh

cd $(realpath $(dirname $0))

if [ -z $1 ]; then
    echo "Usage: $0 <TAG>"
    exit 1
fi

REPO=tokenserver
TAG="$1"

TMPDIR=$(realpath $(mktemp -d TOKEN-XXXXXX))
chmod 755 $TMPDIR

# Extract /app out as a tarball to be ADDed into 
# the busybox distro
echo "=================================="
echo "EXTRACTING /app from docker image: $REPO:$TAG"
echo "=================================="
docker run -v "$TMPDIR:/tmp/output" "$REPO:$TAG" \
    bash -c 'cd /app; tar -zcf /tmp/output/app.tar.gz .'

# Build the slimmed down busybox image
echo 
echo "=================================="
echo "BUILDING MICRO IMAGE FOR PRODUCTION"
echo "=================================="
mv $TMPDIR/app.tar.gz .
docker build -t "$REPO:$TAG-prod" .

echo 
echo "=================================="
echo "TESTING TOKENSERVER IN MICRO IMAGE"
echo "=================================="
docker run -it --rm "$REPO:$TAG-prod" sh -c 'cd /app; ./bin/nosetests tokenserver/tests'

echo 
echo "=================================="
echo "CLEANING UP"
echo "=================================="
rm -rf $TMPDIR
rm app.tar.gz

