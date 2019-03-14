#Serialize/deserialize python data structures with security checks
#pickle library cannot be used because there is no way to ensure security during deserialization

#Each data block is converted to bytes, and prefixed with the data type and byte length

#During deserialization, data structure and data range will be checked for security 

#Everything here will be critical for safe data exchange 

class Serialize():
    TYPE_PREFIX_LENGTH = 1
    SIZE_PREFIX_LENGTH = 3
    
    DATA_STR_TYPE = 0
    DATA_INT_TYPE = 1
    DATA_BOOL_TYPE = 2
    DATA_LIST_TYPE = 3
    DATA_DICT_TYPE = 4
    
    #dictionary of supported types
    types_list = {"<class 'str'>":DATA_STR_TYPE, "<class 'int'>":DATA_INT_TYPE, "<class 'bool'>":DATA_BOOL_TYPE,
                  "<class 'list'>":DATA_LIST_TYPE, "<class 'dict'>":DATA_DICT_TYPE
    }
    
    def new_buffer():
        complete_message = bytearray(b'')
    
    #convert some value to bytes and add it to some data buffer
    def write_value(buffer, val):
        if type(val) is str:
            value_bytes = val.encode('utf-8')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        elif type(val) is int:
            value_bytes = val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        elif type(val) is bool:
            value_bytes = bytearray(b'1') if val else bytearray(b'0')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        buffer += (len(value_bytes)).to_bytes(Serialize.SIZE_PREFIX_LENGTH, byteorder='big')
        buffer += value_bytes
    
    def read_value(buffer, start_idx):
        data_type = int.from_bytes(buffer[start_idx:start_idx+Serialize.TYPE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.TYPE_PREFIX_LENGTH
        data_length = int.from_bytes(buffer[start_idx:start_idx+Serialize.SIZE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.SIZE_PREFIX_LENGTH
        if data_type == Serialize.DATA_STR_TYPE:
            val = buffer[start_idx:start_idx+data_length].decode('utf-8')
        elif data_type == Serialize.DATA_INT_TYPE:
            val = int.from_bytes(buffer[start_idx:start_idx+data_length], byteorder='big')
        elif data_type == Serialize.DATA_BOOL_TYPE:
            val = True if buffer[start_idx:start_idx+1] == bytearray(b'1') else False
        start_idx += data_length
        return val, start_idx
    
    def to_bytes(val):
        buffer = bytearray(b'')
        Serialize.write_value(buffer, val)
        return buffer
        
    def from_bytes(bytes_array):
        val, _ = Serialize.read_value(bytes_array, 0)
        return val

def test_identity(value):
    new_value = Serialize.from_bytes( Serialize.to_bytes(value) )
    if new_value != value:
        print("Identity FAILED", value)

if __name__ == '__main__':
    #Test that we obtain the same value after serialization/deserialization
    test_identity("")
    test_identity("a")
    test_identity("abcdefghij")
    test_identity("test\n\n\t\\\\test")
    test_identity(0)
    test_identity(123450)
    test_identity(11111111111112222222222222233333333333333)
    test_identity(True)
    test_identity(False)
