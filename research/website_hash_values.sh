#!/bin/bash

PAGES=("https://arstechnica.com/science/2022/04/nasas-big-rocket-faces-its-last-test-before-launching/"
	"https://www.npr.org/2022/03/22/1088113080/can-nuclear-power-save-a-struggling-coal-town"
	"https://www.nytimes.com/2022/03/31/world/europe/us-sanctions-russia.html")

for value in "${PAGES[@]}"
do
	echo "$(date --iso-8601=second)| $(curl -s $value | sha256sum)"
done
