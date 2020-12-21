# Bibliographies, LaTex-Styles, LaTex Continuous Integration

*Copy this file to your research-paper projects so you don't forget the below to-dos.*

Stuff to do for each work:

- [ ] Update to latest sosy-paper and sosy-common versions from tex-repo
- [ ] Update to latest .bib files from tex-repo
- [ ] Add OrcIDs for each author
- [ ] Track bbl-file in Git
- [ ] Add section "Data Availability Statement" after Conclusion.
- [ ] Add statement for grant (for camera-ready versions only), for example,
      \blfootnote{Funded in part by the Deutsche Forschungsgemeinschaft (DFG)
      -- \href{https://gepris.dfg.de/gepris/projekt/418257054}{418257054} (Coop)}
- [ ] Add statement for replication package, for example,
      \thanks{A replication package is available on Zenodo~\cite{COVERITEST-artifact-STTT}.}


Stuff to do before publication (or right after):

- [ ] Check that all links work. c.f [the tooling section in Springer-Proof-Issues.txt](Springer-Proof-Issues.txt) for a linkchecker
- [ ] Check pagebreaks, figure placement, and general form (cf. [our English guidelines](https://gitlab.com/sosy-lab/admin/chair/-/wikis/English) and [our paper-writing guide](https://gitlab.com/sosy-lab/admin/chair/-/wikis/PapersHowToTechnical))
- [ ] Upload [replication artifacts](https://gitlab.com/sosy-lab/admin/chair/-/wikis/Replication-Artifacts)
      and check that the publication references the correct DOI
- [ ] Upload preprint to https://sosy-lab.org/research/pub/ (through [lab repository](https://svn.sosy-lab.org/web/lab))
- [ ] Add bib-entry to both [bib/dbeyer.bib](bib/dbeyer.bib) and the corresponding file in [bib/web/](bib/web/);
      Use correct keywords
- [ ] Add news about accepted paper and available preprint to [the news list](https://svn.sosy-lab.org/web/lab/news/news_list.php) in our lab repository

Stuff to do **at least** after each finished submission and publication:

- [ ] Add submitted/published PDF to repository of that publication (according to [the repository organisation](https://gitlab.com/sosy-lab/admin/chair/-/wikis/PapersHowToTechnical#repository-organization))
- [ ] Sync sosy-paper sosy-common versions to tex-repo
- [ ] Sync .bib files to tex-repo
