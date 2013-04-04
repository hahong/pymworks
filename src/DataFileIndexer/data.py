#
#  mworks/data.py
#  DataFileIndexer
#
#  Created by David Cox on 8/17/09.
#  Copyright (c) 2009 Harvard University. All rights reserved.
#

from _data import Event, _MWKFile, _MWKStream
import os
import shutil


class FileNotLoadedException(Exception):
    pass
    
class NoValidCodecException(Exception):
    pass
    
class IndexingException(Exception):
    pass


Event.__module__ = __name__  # So help() thinks Event is part of this module


class MWKFile(_MWKFile):
    # Properties ----------------------------------
    RESERVED_CODEC_CODE = 0
    RESERVED_SYSTEM_EVENT_CODE = 1
    RESERVED_COMPONENT_CODEC_CODE = 2
    RESERVED_TERMINATION_CODE = 3
    N_RESERVED_CODEC_CODES = 4


    # Methods --------------------------------------
    def __init__(self, file_name):
        _MWKFile.__init__(self, file_name)
        self._new_codes = []    # new codes with event blocks to be written
        self._codec = None 
        self._reverse_codec = None 
        self._s_tmp = None      # temporary MWKStream 
        self._s_mwk = None      # original MWKStream 


    def close(self):
        super(MWKFile, self).close()
        self._codec = None
        self._reverse_codec = None 
        self._s_tmp = None
        self._s_mwk = None

    def get_events(self, **kwargs):
        event_codes = []
        time_range = []
    
        # shortcut to argument-free version
        if "codes" not in kwargs and "time_range" not in kwargs:
            return self._fetch_all_events()
    
        codec = self.codec
        
        if codec is None:
            raise NoValidCodecException
            
        reverse_codec = self.reverse_codec
         
        if reverse_codec is None:
            raise NoValidCodecException
    
        if "codes" in kwargs:
            event_codes = kwargs["codes"]
            
            for i in range(0, len(event_codes)):
                code = event_codes[i]
                if(type(code) == str):
                    if(code in reverse_codec):
                        event_codes[i] = reverse_codec[code]
            
        else:
            event_codes = codec.keys()  # all events
        
        if "time_range" in kwargs:
            time_range = kwargs["time_range"]
        else:
            time_range = [self.minimum_time, self.maximum_time]
    
        # TODO: convert possible string-based event codes
    
        events = self._fetch_events(event_codes, time_range[0], time_range[1])
        
        return events
    
    @property
    def codec(self):
        if not self.loaded:
            raise FileNotLoadedException
        if self._codec != None:
            return self._codec
    
        e = self._fetch_events([0])
        if(len(e) == 0):
            self._codec = {}
            return self._codec
        
        raw_codec = e[0].value
        
        codec = {}
        for key in raw_codec.keys():
            codec[key] = raw_codec[key]["tagname"]
        self._codec = codec
        return codec
    
    @property
    def reverse_codec(self):
        if not self.loaded:
            raise FileNotLoadedException
        if self._reverse_codec != None:
            return self._reverse_codec
    
        c = self.codec
        keys = c.keys()
        values = c.values()
        rc = {}
        for i in range(0, len(keys)):
            k = keys[i]
            v = values[i]
            #print("key: %d, value %s" % (k,v))
            rc[v] = k

        self._reverse_codec = rc
        return rc
    
    def reindex(self):
        self.close()
        self.unindex()
        self.open()
    
    # erases all contents in the directory except the original mwk file.
    def empty_dir(self):    # original DDC's unindex().
        if(os.path.isdir(self.file)):
            split_file_name = os.path.split(self.file)
            file_name = split_file_name[-1:][0]
            parent_path = os.pathsep.join(split_file_name[0:-1])
            
            true_mwk_file = os.path.join(self.file, file_name)
                
            print "parent_path: ", parent_path
            print "file_name: ", file_name
            print "true_mwk_file; ", true_mwk_file
            
            aside_path =  os.path.join(parent_path, file_name + ".aside")
            
            os.rename(self.file, aside_path)
            #print "rename %s to %s" % ( self.file, aside_path)
            
            os.rename(os.path.join(aside_path, file_name), os.path.join(parent_path,file_name) )
            #print "rename %s to %s" % ( os.path.join(aside_path, file_name), os.path.join(parent_path,file_name) )
            
            shutil.rmtree(aside_path, True)        # del tree ignoring errors
            #print "remove %s" % aside_path
            
        else:
            raise IndexingException("Attempt to re-index a file that has not yet been indexed")
        

    def unindex(self, empty_dir=False):
        if empty_dir:   # erase all files except .mwk
            self.empty_dir()
            return True
        if not os.path.isdir(self.file): return False

        # only erase the .idx file
        file_name = os.path.basename(self.file)
        idx_file = os.path.join(self.file, file_name + '.idx')
        if os.path.isfile(idx_file):
            os.remove(idx_file)
            return True
        else:
            return False


    # creates a backup of the mwk file 
    def make_backup(self, backup_name=None, close_before=True):
        file_name = os.path.basename(self.file)
        if backup_name is None:
            from datetime import datetime
            # time_str = '.YYYYmmdd_HHMMSS'
            time_str = datetime.now().strftime('.%Y%m%d_%H%M%S')
            backup_name = file_name + time_str + '.bak'

        if close_before and self.loaded: self.close()
        
        true_mwk_file = os.path.join(self.file, file_name)
        if not os.path.isdir(self.file):
            self.close()
            os.rename(self.file, self.file + '.tmp')
            os.mkdir(self.file)
            os.rename(self.file + '.tmp', true_mwk_file)

        shutil.copy(true_mwk_file, os.path.join(self.file, backup_name))


    # revert to one of the backups
    def revert_to(self, desired_backup, make_backup=True, unindex=True):
        desired_backup_fullpath = os.path.join(self.file, desired_backup)
        if not os.path.isfile(desired_backup_fullpath): return False

        if self.loaded: self.close()
        if make_backup: self.make_backup()

        file_name = os.path.basename(self.file)
        true_mwk_file = os.path.join(self.file, file_name)
        os.unlink(true_mwk_file)
        shutil.copy(desired_backup_fullpath, true_mwk_file)

        if unindex: self.unindex()
        return True


    # list all backup files
    def list_backups(self, pattern='*.bak'):
        import fnmatch
        if not os.path.isdir(self.file):
            return []

        backups = []
        for f in os.listdir(self.file):
            if fnmatch.fnmatch(f, pattern):
                backups.append(os.path.basename(f))

        return backups


    def queue_code(self, code=None, code_metadata=None, compact_id=None,
                         event_blocks=None):
        """queue_code(code=None, code_metadata=None, compact_id=None,
            event_blocks=None)
            Put a new code with event blocks to the writing queue.

            Parameters
            ----------
            code: integer, optional
                Codec number to use.  By default `code` is None, (current
                biggest code) + 1 is used.
            code_metadata: dictionary, optional
                Metadata to use. Only the following keys will be referenced:
                    `defaultvalue`, `domain`, `editable`, `groups`, `logging`,
                    `longname`, `nvals`, `persistant`, `shortname`, `tagname`,
                    `viewable`
            compact_id: integer, optional
                Compact id to use.  If None, no information will be written to
                the corresponding compact_id section of the .mwk file.
            event_blocks: list, optional
                Actual data to be written.  Each element should be 2-tuple as
                in the following way: 
                    event_blocks = [(time stamp 1, data 1), (ts 2, data 2), ...]
        """
        new_event_block = {}
        if not self.loaded: self.open()

        if code is None:
            code = max(self.codec.keys() + \
                        [x['code'] for x in self._new_codes]) + 1

        if code_metadata is None:
            code_metadata = {}

        from datetime import datetime
        new_tag_name = datetime.now().strftime('newvar_%Y%m%d_%H%M%S') 
        necessary_keys = ['defaultvalue', 'domain', 'editable', 'groups',
                           'logging', 'longname', 'nvals', 'persistant',
                           'shortname', 'tagname', 'viewable']
        default_values = [0,  # for defaultvalue
                          0,  # for domain: 0 = M_GENERIC_MESSAGE_DOMAIN
                          1,  # for editable
                          ['# ALL VARIABLES'],  # groups
                          4,  # for logging
                          new_tag_name,  # for longname
                          0,  # for nvals
                          1,  # for persistant
                          new_tag_name,  # for shortname
                          new_tag_name,  # for tagname
                          1]  # for viewable
        # remove all unnecessary keys
        for key in code_metadata:
            if not key in necessary_keys:
                del code_metadata[key]
        # add all necessary keys
        def assign_needed(k, v):
            if not code_metadata.has_key(k): code_metadata[k] = v
        map(assign_needed, necessary_keys, default_values) 

        self._new_codes.append({'code':code, 'metadata':code_metadata,
                                'compact_id':compact_id, 'data':event_blocks})
        return code




    def write_queued_codes(self, make_backup=True, backup_name=None,
                           delayed_writing=False, _debug=False, _force_copy=False):
        if not self.loaded: return False
        if not _force_copy and len(self._new_codes) == 0: return False
        if make_backup: self.make_backup(backup_name=backup_name)

        file_name = os.path.basename(self.file)
        tmp_name = file_name + '.tmp'
        true_mwk_file = os.path.join(self.file, file_name)
        true_tmp_file = os.path.join(self.file, tmp_name)
        self.close()

        # initialize stuffs...
        MWKStream._scarab_create_file(true_tmp_file)
        s_mwk = MWKStream('ldobinary:file://' + true_mwk_file)
        s_tmp = MWKStream('ldobinary:file://' + true_tmp_file)
        s_mwk.open()
        s_tmp.open()

        done_compact_id_sect = True      # finished compact_id section?
        done_code_sect = False          # finished code section?
        new_codes = self._new_codes

        for new_code in new_codes:
            if new_code['compact_id'] != None:
                done_compact_id_sect = False
                break

        # start the job -----------------------------------------------
        # handle the headers
        while True:
            if done_code_sect and done_compact_id_sect: break
            ev = s_mwk.read_event()

            # handle compact_id events
            if not done_compact_id_sect and \
                    ev.code == MWKFile.RESERVED_COMPONENT_CODEC_CODE:
                raw_cptid = [ev.code, ev.time]
                raw_cptid_val = ev.value  # this should be dict
                if type(raw_cptid_val) == dict:
                    for new_code in new_codes:
                        if new_code['compact_id'] is None: continue
                        raw_cptid_val[new_code['compact_id']] = \
                            new_code['metadata']['tagname']
                    raw_cptid.append(raw_cptid_val)
                    s_tmp._scarab_write(raw_cptid)
                    done_compact_id_sect = True
                    continue

            # handle code events
            elif not done_code_sect and \
                    ev.code == MWKFile.RESERVED_CODEC_CODE:
                raw_code = [ev.code, ev.time]
                raw_code_val = ev.value   # this should be dict
                if type(raw_code_val) == dict:
                    for new_code in new_codes:
                        raw_code_val[new_code['code']] = new_code['metadata']
                    raw_code.append(raw_code_val)
                    s_tmp._scarab_write(raw_code)
                    done_code_sect = True
                    continue

            # otherwise, just copy the data
            s_tmp._write_event(ev)

        self._s_mwk = s_mwk
        self._s_tmp = s_tmp
        self._true_mwk_file = true_mwk_file
        self._true_tmp_file = true_tmp_file
        
        # put the new event blocks ----------------------------
        for new_code in new_codes:
            event_blocks = new_code['data']
            if event_blocks == None: continue  # user will write events later

            code = new_code['code']
            for ev in event_blocks:
                self.write_one_event(code, ev[0], ev[1])
        s_tmp._scarab_session_flush()

        # if delayed_writing is True, user will write event blocks later.
        # otherwise, write the rest things and finish the operation.
        if not delayed_writing:
            # start dead copy 
            self.finish_writing_codes(_debug=_debug)

        return True


    def write_one_event(self, code, ts, payload):
        raw_event = [code, ts, payload]
        self._s_tmp._scarab_write(raw_event)


    def finish_writing_codes(self, _debug=False):
        s_mwk = self._s_mwk
        s_tmp = self._s_tmp
        BUF_SZ = 1048576

        while True:
            buf = s_mwk._scarab_session_read(BUF_SZ)
            s_tmp._scarab_session_write(buf)
            if len(buf) != BUF_SZ: break   # reached EOF
        s_tmp._scarab_session_flush()

        s_mwk.close()
        s_tmp.close()
        self.unindex()
        self._new_codes = []

        if not _debug:
            os.unlink(self._true_mwk_file)
            os.rename(self._true_tmp_file, self._true_mwk_file)
            self.open()


class MWKStream(_MWKStream):

    def read_event(self):
        result = self._read_event()
        if(result.empty):
            result = None
        return result
