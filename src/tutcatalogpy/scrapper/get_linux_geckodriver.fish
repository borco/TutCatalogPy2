#!/usr/bin/env fish

function effective_url
    curl $argv[1] -s -L -I -o /dev/null -w '%{url_effective}'
end

function github_release
    echo (string split -m1 -r / $argv[1])[2]
end

mkdir -p drivers
pushd drivers

set PLATFORM "linux64.tar.gz"
set RELEASE_URL (effective_url https://github.com/mozilla/geckodriver/releases/latest)
set VERSION (github_release $RELEASE_URL)
set ARCHIVE "geckodriver-$VERSION-$PLATFORM"
set ARCHIVE_URL "https://github.com/mozilla/geckodriver/releases/download/$VERSION/$ARCHIVE"
set PROGRAM geckodriver

# download archive
curl -LO $ARCHIVE_URL

# extract
tar -xvzf $ARCHIVE

# make driver executable
chmod u+x $PROGRAM

# remove archive
rm $ARCHIVE

popd
