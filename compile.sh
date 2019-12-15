#!/bin/bash

pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
cd output
bibtex main1-blx
bibtex main2-blx
bibtex main3-blx
bibtex main4-blx
bibtex main5-blx
bibtex main6-blx
bibtex main7-blx
cd ..
pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
pdflatex -output-directory=output main
