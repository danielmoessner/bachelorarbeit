*.bib files contain all publications of SoSy-Lab (dbeyer's in db* and the others in others.bib)
*.tex files are used to compile bbl files for inclusion in CV, grant proposals, etc.

db:		 conference papers
db-Books:	 books and proceedings
db-INV:		 invited book chapters
db-J:		 journal papers
db-TR:		 technical reports
db-WS:		 workshop papers
others:		 papers of students without dbeyer as co-author
db-sosy-thesis-phd: PhD theses that dbeyer supervised
db-sosy-thesis-msc: MSc theses that dbeyer supervised
db-sosy-thesis-bsc: BSc theses that dbeyer supervised

mkbibhtml.sh is the script that generates the publication lists into folder bib/
bibtex2html-1.02 is the general generator tool

mkbibhtml.sh is automatically executed (and thus the publication lists are updated)
after each push to this repository.

mkbibhtml-cpachecker.sh is the script that generates the publication list
for the CPAchecker website (https://cpachecker.sosy-lab.org/publications.php).
It needs to be executed manually, and afterwards copy CPACHECKER.php
to /html/publications.php in the CPAchecker repository.

Get largest pub number:
grep "%%[0-9]" *bib | cut -d : -f 2 | sed "s/%//g" | sort -n


