#!/bin/sh

TEST_URL=http://127.0.0.1:5000

curl $TEST_URL -s > /dev/null
if [[ $? != 0 ]] ; then
  echo "Server is not running."
  exit -1
fi

echo "Please run tests with a fresh/clean database (rm server/tmp.db)"
echo "Otherwise tests will fail"

for x in tests/* ; do
  pyresttest $TEST_URL $x
done
