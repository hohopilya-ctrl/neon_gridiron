extends Node
class_name MsgPack

# A lite MsgPack decoder for GDScript 2.0 (Godot 4.6)
# Supports: Nil, Bool, Int, Float (32/64), String, Map, Array, Binary

static func unpack(bytes: PackedByteArray) -> Variant:
	var stream = StreamPeerBuffer.new()
	stream.data_array = bytes
	return _unpack_next(stream)

static func _unpack_next(stream: StreamPeerBuffer) -> Variant:
	if stream.get_available_bytes() == 0: return null
	
	var type = stream.get_u8()
	
	# Positive FixInt
	if type <= 0x7f: return type
	
	# FixMap
	if type >= 0x80 and type <= 0x8f:
		return _unpack_map(stream, type & 0x0f)
		
	# FixArray
	if type >= 0x90 and type <= 0x9f:
		return _unpack_array(stream, type & 0x0f)
		
	# FixStr
	if type >= 0xa0 and type <= 0xbf:
		return _unpack_string(stream, type & 0x1f)
		
	# Nil
	if type == 0xc0: return null
	
	# Unused 0xc1
	
	# Bool
	if type == 0xc2: return false
	if type == 0xc3: return true
	
	# Bin
	if type == 0xc4: return _unpack_bin(stream, stream.get_u8())
	if type == 0xc5: return _unpack_bin(stream, stream.get_u16())
	if type == 0xc6: return _unpack_bin(stream, stream.get_u32())
	
	# Float
	if type == 0xca: return stream.get_float()
	if type == 0xcb: return stream.get_double()
	
	# Int (Unsigned)
	if type == 0xcc: return stream.get_u8()
	if type == 0xcd: return stream.get_u16()
	if type == 0xce: return stream.get_u32()
	if type == 0xcf: return stream.get_u64()
	
	# Int (Signed)
	if type == 0xd0: return stream.get_8()
	if type == 0xd1: return stream.get_16()
	if type == 0xd2: return stream.get_32()
	if type == 0xd3: return stream.get_64()
	
	# String
	if type == 0xdb: return _unpack_string(stream, stream.get_u32())
	
	# Array
	if type == 0xdc: return _unpack_array(stream, stream.get_u16())
	if type == 0xdd: return _unpack_array(stream, stream.get_u32())
	
	# Map
	if type == 0xde: return _unpack_map(stream, stream.get_u16())
	if type == 0xdf: return _unpack_map(stream, stream.get_u32())
	
	# Negative FixInt
	if type >= 0xe0:
		return type - 256
		
	return null

static func _unpack_string(stream: StreamPeerBuffer, length: int) -> String:
	return stream.get_utf8_string(length)

static func _unpack_bin(stream: StreamPeerBuffer, length: int) -> PackedByteArray:
	return stream.get_data(length)[1]

static func _unpack_array(stream: StreamPeerBuffer, size: int) -> Array:
	var arr = []
	for i in range(size):
		arr.append(_unpack_next(stream))
	return arr

static func _unpack_map(stream: StreamPeerBuffer, size: int) -> Dictionary:
	var dict = {}
	for i in range(size):
		var key = _unpack_next(stream)
		var val = _unpack_next(stream)
		dict[key] = val
	return dict
