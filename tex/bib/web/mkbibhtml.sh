#!/bin/bash

# Do not silently ignore errors
set -euo pipefail

mkdir --parents bib || true;
cd bib
rm -r  index.html Author All Category Keyword Year || true

../bibtex2html-1.02 -force -html-links -sort year \
       ../db.bib \
       ../db-Books.bib \
       ../db-INV.bib \
       ../db-J.bib \
       ../db-TR.bib \
       ../db-WS.bib \
       ../db-Software.bib \
       ../ernst.bib \
       ../others.bib \
       ../db-sosy-theses-phd.bib \
       ../db-sosy-theses-msc.bib \
       ../db-sosy-theses-bsc.bib \
       ../db-sosy-theses-projects.bib \
       ../ernst-sosy-theses-phd.bib \
       ../ernst-sosy-theses-msc.bib \
       ../ernst-sosy-theses-bsc.bib \
       ../ernst-sosy-theses-projects.bib \
       ../mcb-sosy-theses-bsc.bib \
       ../db.cfg \

# Change headings in HTML pages
find . -name "*.html" \
  -exec sed -i {} \
    -e "s/Conference articles/Articles in conference or workshop proceedings/" \
    -e "s/Miscellaneous/Theses and projects (PhD, MSc, BSc, Project)/" \
  \;

sed -i 's/Selection by keyword/\<a name\=research_interests\>\<\/a\>Selection by research interest/' index.html
#WPATH="http://www.sosy-lab.org/~dbeyer/Publications/bib"
#find . -name "*.html" -exec sed -i "s*\$W/*$WPATH/*" {} \;
