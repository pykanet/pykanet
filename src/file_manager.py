
import hashlib
import os

from serialization_utils import Serialize

#Interface to the host file system
#All "file accesses" should be done through this class
#It will allow in the future to cache data, and also reorganize it and store it efficiently 
class FileManager():
    
    #should be called only once when application is started
    #return True if initialization was successful
    def init_save_path():
        FileManager.root_dir = "pykanet_data/"
        FileManager.index_file = FileManager.root_dir + "index"
        
        if not os.path.exists(FileManager.root_dir):
            try:
                os.makedirs(FileManager.root_dir)
            except:
                #save directory does not exist and could not be created
                return False
        
        #structure to keep a track of all files existing on the local node
        if os.path.isfile(FileManager.index_file):
            FileManager._read_index()
        else:
            FileManager.local_index = {}
        
        return True
    
    def _read_index():
        FileManager.local_index = Serialize.from_bytes(FileManager._raw_file_read(FileManager.index_file))
    
    def _write_index():
        FileManager._raw_file_write(FileManager.index_file, Serialize.to_bytes(FileManager.local_index))
    
    #update the index of all files when a file is written
    def _update_index_file_write(network_path):
        #currently, only keep a track of existing files
        if network_path not in FileManager.local_index:
            FileManager.local_index[network_path] = FileManager.get_file_name(network_path)
            FileManager._write_index()
    
    def get_file_name(network_path):
        return FileManager.root_dir + hashlib.sha224(network_path.encode('utf-8')).hexdigest()
    
    def file_exists(network_path):
        filename = FileManager.get_file_name(network_path)
        return os.path.isfile(filename)
    
    def _raw_file_read(filename):
        try:
            with open(filename, "rb") as file:
                return file.read()
        except:
            #could not read the file (probably file not existing yet)
            return None
    
    def _raw_file_write(filename, new_content):
        try:
            with open(filename, "wb") as file:
                file.write(new_content)
            return True
        except:
            print("Warning: an error occurred when writing data to:", filename)
            return False
    
    def file_read(network_path):
        filename = FileManager.get_file_name(network_path)
        try:
            with open(filename) as file:
                return file.read()
        except:
            #could not read the file (probably file not existing yet)
            return None
    
    #TODO: for efficiency, some cache mechanism could be used
    #return True if writing was successful
    def file_write(network_path, new_content):    
        FileManager._update_index_file_write(network_path)
        
        filename = FileManager.get_file_name(network_path)
        try:
            with open(filename, "w") as file:
                file.write(new_content)
            return True
        except:
            print("Warning: could not open file ", filename, "to save data of ", network_path)
            return False
    
    #TODO: for efficiency, some cache mechanism could be used
    def file_append(network_path, added_content):
        filename = FileManager.get_file_name(network_path)
        try:
            with open(filename, "a") as file:
                file.write(added_content)
        except:
            print("Warning: could not open file ", filename, "to save data of ", network_path)
