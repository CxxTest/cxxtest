
html: guide.txt anchors
	a2x -a latexmath -a docinfo -k -L -d article -f xhtml -v guide.txt

anchors:
	python include_anchors.py guide.txt 

clean:
	- \rm book.xml
	- \rm examples/*_*.py examples/*_*.h examples/*_*.cpp examples/*_*.sh examples/runner examples/runner.cpp

