SPHINXBASE_PATH=/home/bshanks/prog/speech/sphinxbase
SPHINX3_PATH=/home/bshanks/prog/speech/sphinx3

all: fakekey_uinput word-vocab.arpa.DMP keyboard-vocab.arpa.DMP view-vocab.arpa.DMP 

clean:
	rm sphinx3_livesegment fakekey_uinput word-vocab.arpa.DMP keyboard-vocab.arpa.DMP view-vocab.arpa.DMP

sphinx3_livesegment: sphinx3_livesegment.c
	gcc sphinx3_livesegment.c -I$(SPHINXBASE_PATH)/include -I$(SPHINX3_PATH)/include -lsphinxad -ls3decoder -lm -o sphinx3_livesegment

fakekey_uinput: fakekey_uinput.c
	gcc fakekey_uinput.c -o fakekey_uinput

word-vocab.arpa.DMP: word-vocab.arpa
	rm -f  word-vocab.arpa.DMP
	lm3g2dmp word-vocab.arpa .

keyboard-vocab.arpa.DMP: keyboard-vocab.arpa
	rm -f  keyboard-vocab.arpa.DMP
	lm3g2dmp keyboard-vocab.arpa .

view-vocab.arpa.DMP: view-vocab.arpa
	rm -f  view-vocab.arpa.DMP
	lm3g2dmp view-vocab.arpa .

savespace:
	rm *.arpa
