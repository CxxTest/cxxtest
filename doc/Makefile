.PHONY: all anchors outputs clean

export XML_CATALOG_FILES = catalog.xml
XSLTPROC_OPTS := --stringparam toc.section.depth 2 --stringparam generate.section.toc.level 1
DBLATEX_OPTS  := -P latex.output.revhistory=0 -P doc.collab.show=1 -P toc.section.depth=2
A2X_OPTS      := -a toc -L -d article -v --xsltproc-opts "$(XSLTPROC_OPTS)" --dblatex-opts "$(DBLATEX_OPTS)"

%.html: %.txt anchors outputs
	asciidoc -v -d article -n -a toc2 $<

# Ignore errors (dblatex may not be installed)
%.pdf: %.txt anchors outputs
	- a2x -f pdf $(A2X_OPTS) $<

# Ignore errors
%.epub: %.txt anchors outputs
	- a2x -f epub $(A2X_OPTS) $<

all: guide.html guide.pdf guide.epub

anchors: guide.txt
	python include_anchors.py $<

outputs: examples/cxxtestgen.out

examples/cxxtestgen.out: ../bin/cxxtestgen
	- $< -h && $< -h > $@

clean:
	- \rm -f guide.xml
	- \rm -f examples/.*.py examples/.*.h examples/.*.cpp examples/.*.sh examples/runner examples/TEST*.xml examples/parsetab.py examples/*.orig examples/runner.cpp

