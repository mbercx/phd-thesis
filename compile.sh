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

num_chapters=`ls -l chapters/ | grep .tex | wc -l`

pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
rsync -av bibliography/ output/bibliography
cd output
makeglossaries main
while [[ $i -le $num_chapters ]]; do 
  bibtex "main$i-blx"
  i=$(($i+1))
done
cd ..
pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
pdflatex -output-dir=output '\PassOptionsToPackage{draft}{graphicx}\input{main}'
pdflatex -output-directory=output main
cp output/main.pdf ./thesis.pdf
