MEM_MODEL=simple
OS_TYPE=unix
STREAMS=file tcpip
ENCODERS=ldo

CC=gcc
CFLAGS=-I.. -I. -DLINUX -D__LITTLE_ENDIAN__ -fPIC -O0

AR=ar

LIBS=-lm

ENCODERS:=$(for i in "$(ENCODERS)"; do echo encoding_$i.o; done)
STREAMS:=$(for i in "$(STREAMS)"; do echo stream_$i.o; done)

HEADERS=\
	encoding_ldo.h \
	scarab.h \
	scarab_datatypes.h \
	scarab_dict.h \
	scarab_list.h \
	scarab_mem.h \
	scarab_os.h \
	scarab_utilities.h

OBJS=\
	os_$(OS_TYPE).o \
	mem_$(MEM_MODEL).o \
	comp.o \
	data.o \
	hashtable.o \
	list.o \
	session.o \
	encoding_ldo.o \
	scarab_utilities.o \
	stream_file.o \
	stream_tcpip.o \
	stream_tcpip_select.o \
	stream_tcpip_buffered.o

.c.o:
	$(CC) $(CFLAGS) -c $<

all: libscarab.a

libscarab.a: $(OBJS) 
	$(AR) rcs libscarab.a $(OBJS)

clean:
	rm -f *~
	rm -f *.o
	rm -f libscarab.a

FORCE:

####################################################

# Generic Library
comp.o: comp.c $(HEADERS)
data.o: data.c $(HEADERS)
hashtable.o: hashtable.c $(HEADERS)
list.o: list.c $(HEADERS)
session.o: session.c $(HEADERS)

# Encoders
encoding_ldo.o: encoding_ldo.c encoding_ldo.h $(HEADERS)

# Operating Systems
os_unix.o: os_unix.c $(HEADERS)

# Memory Models
mem_simple.o: mem_simple.c $(HEADERS)

# Streams
stream_file.o: stream_file.c $(HEADERS)
stream_tcpip.o: stream_tcpip.c $(HEADERS) 
stream_tcpip_select.o: stream_tcpip_select.c $(HEADERS) 
stream_tcpip_buffered.o: stream_tcpip_buffered.c $(HEADERS) 
