
html: guide.txt anchors outputs
	a2x -a latexmath -a docinfo -k -L -d article -f xhtml -v guide.txt

anchors:
	python include_anchors.py guide.txt 

outputs:
	../bin/cxxtestgen -h > examples/cxxtestgen.out

clean:
	- \rm -f guide.xml
	- \rm -f examples/.*.py examples/.*.h examples/.*.cpp examples/.*.sh examples/runner examples/*.cpp examples/TEST*.xml

