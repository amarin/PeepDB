#
# PeepDB v 0.1 "Germ"
# (c) 2001 Alexey Vyskubov alexey@pepper.spb.ru
#
import struct
#import chardet

def to_byte(s):
	return struct.unpack('%sB' % len(s), s)

def from_byte(x):
	return struct.pack('B', x)

def to_word(s):
	assert len(s)==2,'Incorrect dword length: %s of 2' % len(s)
	return struct.unpack('>H', s)[0]

def from_word(x):
	return struct.pack('>H', x)

def to_dword(s):
	assert len(s)==4,'Incorrect dword length: %s of 4' % len(s)
	return struct.unpack('>L', s)[0]

def from_dword(x):
	return struct.pack('>L', x)

def assign_byte(dt, b, offset):
	dt[offset] = b[0]
	return dt

def assign_word(dt, w, offset):
	dt = dt[:offset]+ w + dt[offset+2:]
	return dt

def assign_dword(dt, dw, offset):
	dt = assign_word(dt, dw[0:2], offset)
	dt = assign_word(dt, dw[2:], offset+2)
	return dt

class data_header:
	"Common header manipulation"
	def __init__(self, size):
		self.data = '\0'*size
	
	def __len__(self):
		return len(self.data)
		
	def put_data_byte(self, b, offset):
		self.data = assign_byte(self.data, from_byte(b), offset)
	
	def get_data_byte(self, offset):
		return to_byte(self.data[offset])
	
	def put_data_bit(self, bit, byte_offset, bit_offset):
		newbyte = get_data_byte(byte_offset)
		newbit = 2 ** bit_offset
		if bit == 0:
			newbyte = newbyte & (255 - newbit)
		else:
			newbyte = newbyte | newbit
	
	def get_data_bit(self, byte_offset, bit_offset):
		oldbyte = get_data_byte(byte_offset)
		oldbit = 2 ** bit_offset
		return oldbyte & oldbit

	def put_data_word(self, w, offset):
		self.data = assign_word(self.data, from_word(w), offset)

	def get_data_word(self, offset):
		return to_word(self.data[offset:offset+2])

	def put_data_dword(self, dw, offset):
		self.data = assign_dword(self.data, from_dword(dw), offset)
	
	def get_data_dword(self, offset):
		assert offset>=0,'Incorrect offset "%s"' % offset
		try:
			return to_dword(self.data[offset:offset+4])
		except AssertionError,s:
			raise AssertionError, 'self.data has incorrect length on offset %s' % offset

	def put_data_string(self, str, offset):
		if str.__class__.__name__=='int':
			str='%s' % str
		self.data = self.data[0:offset]+str+self.data[offset+len(str):]
	
	def get_data_string(self, len, offset):
		return self.data[offset:offset+len]


class pdb_header(data_header):
	"PalmOS pdb file header"

	def set_name(self, nm):
		k = len(nm)
		if k > 31:
			self.put_data_string(nm[0:31]+'\0', 0)
		else:
			self.put_data_string(nm+'\0', 0)

	def set_attributes(self, at):
		self.put_data_word(at, 32)

	def get_attributes(self):
		return self.get_data_word(32)
	
	def set_version(self, ver):
		self.put_data_word(ver, 34)
	
	def get_version(self):
		return self.get_data_word(34)
	
	def set_create_time(self, time):
		self.put_data_dword(time, 36)
	
	def get_create_time(self):
		return self.get_data_dword(36)
	
	def set_modify_time(self, time):
		self.put_data_dword(time, 40)
	
	def get_modify_time(self):
		return self.get_data_dword(40)
	
	def set_backup_time(self, time):
		self.put_data_dword(time, 44)
	
	def get_backup_time(self):
		return self.get_data_dword(44)
	
	def set_modification_number(self, num):
		self.put_data_dword(num, 48)

	def get_modification_number(self):
		return self.get_data_dword(48)

	def set_appInfoID(self, id):
		self.put_data_dword(num, 52)
	
	def get_appInfoID(self):
		return self.get_data_dword(52)
	
	def set_sortInfoID(self, id):
		self.put_data_dword(num, 56)
	
	def get_sortInfoID(self):
		return self.get_data_dword(56)
	
	def set_type(self, type):
		self.put_data_string(type, 60)
	
	def get_type(self):
		return self.get_data_string(60)
	
	def set_creator(self, creat):
		self.put_data_string(creat, 64)
	
	def get_creator(self):
		return self.get_data_string(64)
	
	def set_id_seed(self, seed):
		self.put_data_dword(seed, 68)
	
	def get_id_seed(self):
		return self.get_data_dword(68)
	
	def set_next_record_list(self, list):
		self.put_data_dword(list, 72)
	
	def get_next_record_list(self):
		return self.get_data_dword(72)
	
	def set_number_of_records(self, num):
		self.put_data_word(num, 76)
	
	def get_number_of_records(self):
		return self.get_data_word(76)

	def load_from_file(self, filename):
		f = open(filename, 'r')
		self.data = f.read(78)
		f.close()
	
	def get_from_pdb(self, pdb):
		self.data = pdb[0:78]

	def init(self, nm):
		data_header.__init__(self, 78)
		self.set_name(nm)
		self.set_create_time(1000000) # FIXME
		self.set_modify_time(1000000) # FIXME
		self.set_type("NULL")
		self.set_creator("NULL")

	def __init__(self, mode, nm):
		if mode == 'new':
			self.init(nm)
		elif mode == 'load':
			self.load_from_file(nm)
		elif mode == 'get':
			self.get_from_pdb(nm)
		else:
			raise RuntimeError, '%s must init with one of mode: new, load or get'

class record_header(data_header):
	"PDB's record header"
	
	def init(self):
		data_header.__init__(self, 8)
	
	def __init__(self, hdr):
		if hdr == '':
			self.init()
		else:
			self.data = hdr
	
	def set_offset(self, offset):
		self.put_data_dword(offset, 0)

	def get_offset(self):
		assert len(self.data)==8, 'Length of data 4 but %s' % len(self.data)
		return self.get_data_dword(0)

	def set_delete_bit(self, bit):
		self.put_data_bit(self, bit, 4, 7)
	def set_dirty_bit(self, bit):
		self.put_data_bit(self, bit, 4, 6)
	def set_busy_bit(self, bit):
		self.put_data_bit(self, bit, 4, 5)
	def set_secret_bit(self, bit):
		self.put_data_bit(self, bit, 4, 4)
	def set_category(self, cat):
		self.put_data_bit(self, (cat & 8)/8, 4, 3)
		self.put_data_bit(self, (cat & 4)/4, 4, 2)
		self.put_data_bit(self, (cat & 2)/2, 4, 1)
		self.put_data_bit(self, cat & 1, 4, 0)
	
	def set_id(self, id):
		# id is only 3 chal len, so need conwert int(id) into more powerfull system
		chars='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		base = len(chars)
		r1,l1 = divmod(id,base*base)
		r2,r3 = divmod(l1,base)
		char_id = '%s%s%s' % (chars[r1],chars[r2],chars[r3])
		self.put_data_string(char_id, 5)
		
		
	def get_id(self):
		return self.get_data_string(3, 5)

class palmdb:
	"PalmOS pdb format"
	# first offset = 78L + count*8 = 86
	last_offset=86

	def init(self, nm):
		self.main_header = pdb_header('new', nm)
		self.records=[]

	def __init__(self, mode, nm):
		if mode == 'new':
			self.init(nm)
		else:
			self.init('noname')
			if mode == 'load':
				self.load_from_file(nm)
			else:
				if mode == 'get':
					self.get_from_pdb(nm)
				# FIXME
							
	
	
	def shift_offsets(self):
		for rec in range(self.main_header.get_number_of_records()):
			current = self.records[rec][0]
			current.set_offset(current.get_offset()+8)
	
	def unshift_offsets(self):
		for rec in range(self.main_header.get_number_of_records()):
			current = self.records[rec][0]
			current.set_offset(current.get_offset()-8)	
	
	
		
	def clean_all_records(self):
		while (len(self.records)>0):
			rec = self.records.pop()
			del rec[0]

	def get_from_pdb(self, pdb):
		self.clean_all_records()
		self.main_header.get_from_pdb(pdb[0:78])
		skip = 78
		i = self.main_header.get_number_of_records()
		while i > 0:
			self.records.append(['', ''])
			self.records[-1][0] = record_header(pdb[skip:skip+8])
			skip = skip + 8
			i = i - 1
		i = len(self.records) - 1
		while (i >= 0):
			start = int(self.records[i][0].get_offset())
			if i == len(self.records) - 1:
				self.records[i][1] = pdb[start:]
			else:
				end = int(self.records[i+1][0].get_offset())
				self.records[i][1] = pdb[start:end]
			i = i - 1

	def load_from_file(self, filename):
		f = open(filename, 'r')
		pdb = f.read()
		f.close()
		self.get_from_pdb(pdb)

	# FIXME
	def calculate_offsets(self,debug=False):
		# Main PDB's header is 78 bytes
		# Record's header is 8 bytes
		count = self.main_header.get_number_of_records()
		assert count>0, 'Record count==0'
		if debug:
			print 'Count %s' % count
		ot = 78L + count*8
		if debug:
			print 'First on %s' % ot
		for rec in range(count):
			if rec<0 and debug:
				print 'current offset %s' % ot
			self.records[rec][0].set_offset(ot)
			ot = ot + len(self.records[rec][1])
	
	def create_new_record(self, id, data, debug=False):
		# create record
		record = []
		# init header && set id
		header = record_header('')
		header.set_id(id)
		# append header && data into record
		record.append(header)
		record.append(data)
		# put record into records, update header && calculate_offsets
		self.records.append(record)
		self.main_header.set_number_of_records(self.main_header.get_number_of_records() + 1)
		#self.calculate_offsets(debug)
		# set offset of current
		#self.records[-1][0].set_offset(self.last_offset)
		# shift last_offset by len of current
		#self.last_offset+=len(self.records[-1][1])
		# recalc all offsets
		#self.shift_offsets()
	
	def save_to_file(self, filename):
		# calculate offsets
		self.calculate_offsets(True)
		# openfile
		f = open(filename, 'wb')
		f.write(self.main_header.data)
		for i in range(self.main_header.get_number_of_records()):
			txt_rec=self.records[i][1]
			f.write(self.records[i][0].data)
		for i in range(self.main_header.get_number_of_records()):
			txt_rec=self.records[i][1]
			f.write(txt_rec)
		f.close()

		
