#!/bin/bash

if [[ ! -d output ]]; then
  mkdir output
  mkdir output/chapters
fi

if [[ -z `command -v pdflatex` ]]; then
  echo "Error: pdflatex command not found. Is LaTeX installed on your system?"
  exit 1
fi
if [[ -z `command -v makeglossaries` ]]; then
  echo "Error: makeglossaries command not found. Is LaTeX installed on your system?"
  exit 1
fi
if [[ -z `command -v bibtex` ]]; then
  echo "Error: bibtex command not found. Is LaTeX installed on your system?"
  exit 1
fi

pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
rsync -av bibliography/ output/bibliography
cd output
makeglossaries main
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
cp output/main.pdf ./thesis.pdf
