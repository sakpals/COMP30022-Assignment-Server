#!/bin/sh

TEST_URL=http://127.0.0.1:5000

curl $TEST_URL -s > /dev/null
if [[ $? != 0 ]] ; then
  echo "Unable to connect to: $TEST_URL"
  echo "Are you sure the server is running?"
  exit $rc
fi

for x in tests/* ; do
  pyresttest $TEST_URL $x
done

