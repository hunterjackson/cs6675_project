#!/bin/bash

PAGES=("https://arstechnica.com/science/2022/04/nasas-big-rocket-faces-its-last-test-before-launching/"
	"https://www.npr.org/2022/03/22/1088113080/can-nuclear-power-save-a-struggling-coal-town"
	"https://www.nytimes.com/2022/03/31/world/europe/us-sanctions-russia.html")

echo "ipv4 address -> $(curl -s https://ipv4.canhazip.com/)"
for page in "${PAGES[@]}"
do
	echo "$(date --iso-8601=second) [$(sed -nE 's|https://([^/]+)/.*$|\1|p' <(echo $page))] $(curl -s $page | sha256sum)"
done
