CC=g++
CFLAGS=-fPIC -fpermissive -I .. -I ../Scarab -I /usr/include/python2.7 -L ../Scarab -lscarab -O0 -D BOOST_FILESYSTEM_VERSION=2
OBJS=DataFileIndexer.o DataFileUtilities.o EventWrapper.o EventBlock.o dfindex.o PythonDataBindings.o PythonDataBindingsHelpers.o

all: $(OBJS)
	g++ -shared -Wl,-soname,_data.so -o _data.so $(OBJS) ../Scarab/libscarab.a -lpython2.7 -lboost_system-mt -lboost_serialization-mt -lboost_filesystem-mt -lboost_python-mt-py27

DataFileIndexer.o: 
	$(CC) $(CFLAGS) -c DataFileIndexer.cpp

DataFileUtilities.o:
	$(CC) $(CFLAGS) -c DataFileUtilities.cpp

EventBlock.o:
	$(CC) $(CFLAGS) -c EventBlock.cpp

EventWrapper.o:
	$(CC) $(CFLAGS) -c EventWrapper.cpp

dfindex.o:
	$(CC) $(CFLAGS) -c dfindex.cpp

PythonDataBindings.o:
	$(CC) $(CFLAGS) -c PythonDataBindings.cpp

PythonDataBindingsHelpers.o:
	$(CC) $(CFLAGS) -c PythonDataBindingsHelpers.cpp

clean:
	#rm -rf $(INSTALL_DIR)/include/dfindex
	rm -f *~
	rm -f *.o
	rm -f *.so


####################################################
