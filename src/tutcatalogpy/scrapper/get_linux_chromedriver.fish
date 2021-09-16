#!/usr/bin/env fish

mkdir -p drivers
pushd drivers

set ARCHIVE chromedriver_linux64.zip
set PROGRAM chromedriver
set VERSION (curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# download archive
curl -O https://chromedriver.storage.googleapis.com/$VERSION/$ARCHIVE

# extract archive
unzip $ARCHIVE

# make driver executable
chmod u+x $PROGRAM

# remove archive
rm $ARCHIVE

popd
