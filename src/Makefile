all: libscarab.a _data.so
	cp DataFileIndexer/_data.so .

install: all
	cp _data.so ../pymworks/
	rm -f ../pymworks/*.pyc

libscarab.a:
	cd Scarab; make

_data.so:
	cd DataFileIndexer; make

clean:
	cd Scarab; make clean
	cd DataFileIndexer; make clean
	rm -f _data.so
