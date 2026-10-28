# Build the paper PDF (requires TeX Live: pdflatex, bibtex, latexmk)
all: main.pdf
main.pdf: main.tex references.bib
	latexmk -pdf -interaction=nonstopmode main.tex
clean:
	latexmk -C
	rm -f build.log
.PHONY: all clean
