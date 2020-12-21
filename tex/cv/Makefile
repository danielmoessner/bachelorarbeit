## Example Makefile to create HTML page for own publications
## from our chair's .bib files.

# Directory that contains .bib files
BIBS ?= publications

# Create a single HTML list for own publications
# The created HTML has css classes 'pdf', 'pres', 'url' and 'biblinks'
# for styling the links of each bib entry.
#
# The created HTML can be inserted in some HTML skeleton.
# Example: https://thomaslemberger.com/pub/index.html
publications.html: $(BIBS)/lemberger.bib
        bibtex2html --no-abstract --title "Thomas Lemberger (Publications)" \
							  -css publications.css \
							  --dl --sort-by-date --reverse-sort --no-keywords --nodoc \
                --named-field pdf '<span class="pdf">PDF</span>' \
                --named-field postscript '<span class="pres">Presentation</span>'  \
                --named-field url '<span class="url">Web</span>' \
                --output - \
                $(BIBS)/lemberger.bib >> $@
        sed -i -e "/<h1>.*Publications.*<\/h1>/d" \
                -e "s/^\[&nbsp;/<span class='biblinks'>/" \
                -e "s/&nbsp;\]/<\/span>/" \
                -e "s/&nbsp;|//" \
                -e "s/\([0-9]\)--\([0-9]\)/\1\&ndash;\2/g" \
                $@

# This target creates the bib-file of own publications,
# used by bibtex2html above to create the HTML.
$(BIBS)/lemberger.bib: $(BIBS)/db.bib $(BIBS)/db-J.bib
        bib2bib -c 'author : "Lemberger"' \
                --remove editor \
                --remove keyword \
                --remove isbn \
                $(BIBS)/db.bib > $@
        bib2bib -c 'author : "Lemberger"' \
                --remove editor \
                --remove keyword \
                --remove isbn \
                $(BIBS)/db-J.bib >> $@
