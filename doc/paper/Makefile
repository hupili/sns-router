NAME=snsrouter
TEX=$(NAME).tex
PDF=$(NAME).pdf

tutorial:
	#echo $(TEX)
	rm -f $(PDF) 
	cd ../reference/ ; make
	#first run, get .aux
	pdflatex $(NAME)
	#second run, get final output
	#latex $(TEX)
	#dvipdf $(NAME).dvi $(NAME).pdf

TMP_LIST= \
		  *.aux \
		  *.log \
		  *~ \
		  *.toc \
		  *.blg \
		  *.out \
		  *.snm \
		  *.nav \
		  *.dvi

clean:
	rm -f ${TMP_LIST}
	rm -rf tmp
