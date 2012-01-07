
html: guide.txt anchors outputs
	asciidoc -v -b html -d article -n -a toc guide.txt

pdf: guide.txt anchors outputs
	a2x -a toc -L -d article -f pdf -v --dblatex-opts "-P latex.output.revhistory=0 -P doc.collab.show=1 -P toc.section.depth=2" guide.txt

epub: guide.txt anchors outputs
	export XML_CATALOG_FILES=export XML_CATALOG_FILES="catalog.xml"; a2x -L -f epub -d article --verbose --xsltproc-opts "--stringparam toc.section.depth 2 --stringparam generate.section.toc.level 1" guide.txt

all: html pdf epub

anchors:
	python include_anchors.py guide.txt 

outputs:
	../bin/cxxtestgen -h > examples/cxxtestgen.out

clean:
	- \rm -f guide.xml
	- \rm -f examples/.*.py examples/.*.h examples/.*.cpp examples/.*.sh examples/runner examples/TEST*.xml examples/parsetab.py examples/*.orig examples/runner.cpp

