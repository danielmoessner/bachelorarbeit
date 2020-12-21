#!/bin/bash

# Do not silently ignore errors
set -euo pipefail

mkdir --parents cpachecker || true;
cd cpachecker
wget https://svn.sosy-lab.org/software/cpachecker/trunk/doc/cpachecker.bib -O cpachecker.bib

../bibtex2html-1.02 -force -sort year \
       ../db.bib \
       ../db-Books.bib \
       ../db-INV.bib \
       ../db-J.bib \
       ../db-TR.bib \
       ../db-WS.bib \
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
       cpachecker.bib \
       ../db.cfg \
       ../cpachecker.cfg \

find . -name "*.php" \
  -exec sed -i {} \
    -e "s/Conference articles/Articles in conference or workshop proceedings/" \
    -e "s/Miscellaneous/Theses and projects (PhD, MSc, BSc, Project)/" \
  \;

mv Keyword/CPACHECKER.php ../
recode iso8859-1..utf8 ../CPACHECKER.php
