#!/bin/bash

SITE=$1
echo "website -> $1"
fingerprint=`curl -s $SITE | sha256sum -t`
ts=`date --iso-8601=seconds`

echo "$ts| $fingerprint" 

new_fingerprint=`curl -s $SITE | sha256sum -t`

while [[ $fingerprint = $new_fingerprint ]] 
do
	new_fingerprint=`curl -s $SITE | sha256sum -t`
	sleep 5s
done

ts=`date --iso-8601=seconds`
echo "$ts| $new_fingerprint"
