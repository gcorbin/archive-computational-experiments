#!/bin/bash
# Look in all description files(<project>*/description) for matching tags
# print only those files that have all tags
# a tag is a whole word that starts with #

if [ $# -lt 1 ]
then
  echo "usage: find_tags.sh <project> [tag ...]"
  exit 
fi
project=$1
echo "Files that have all of the following tags: ${@:2}"
echo ""
filter="$1*/description"
for tag in "${@:2}"
do
    filter=$(grep -rlw "#$tag" $filter)
done
for item in $filter
do
    echo $item
done
