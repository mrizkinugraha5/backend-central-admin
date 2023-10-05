import mysql.connector
from . import config

# pyDict -> paramater where berupa dictionary python
# myDict -> paramater where berupa list dengan kolom, tanda, dan values dipisah spasi contoh ['id = 1', 'stok > 10']

class Database:
	def __init__(self):
		self.mydb = dbConn()

	def get_data(self, query, values):
		return select(query, values, self.mydb)
	
	def insert_data(self, query, values):
		return inup(query, values, self.mydb)
	
	def update_data(self, query, values):
		return inup(query, values, self.mydb)

	def execute(self, query):
		return execute_sql(query, self.mydb)

	def save(self, table, data):
		col = ', '.join(data.keys()) # data = dict()
		nval = "%s" + ", %s" * (len(data)-1)
		query = f"INSERT INTO {table} ({col}) VALUES ({nval})"
		values = list(data.values())
		inup(query, values, self.mydb)
	
	def saveReturn(self, table, data):
		# fungsi insert + mengembalikan id 
		col = ', '.join(data.keys()) # data = dict()
		nval = "%s" + ", %s" * (len(data)-1)
		query = f"INSERT INTO {table} ({col}) VALUES ({nval})"
		values = tuple(data.values())
		return insert2(query, values, self.mydb)


# Build database connection
def dbConn(user=config.DB_USER, password=config.DB_PASSWORD, host=config.DB_HOST, database=config.DB_NAME):
    db = mysql.connector.connect (
		host=host,
		user=user,
		password=password,
		database=database
	)
    return db

# Get all row
def selall(query, values, conn):
	mycursor = conn.cursor(buffered=True)
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	myresults = mycursor.fetchall()
	json_data = []
	if myresults != None:
		for myresult in myresults:
			result = [(x.decode() if type(x)==bytearray else x) for x in myresult] # decode bytearray
			json_data.append(dict(zip(row_headers, result)))
		return json_data
	else:
		return None

# Get single row
def selrow(query, values, conn):
	mycursor = conn.cursor(buffered=True)
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchone()
	if myresult != None:
		result = [(x.decode() if type(x)==bytearray else x) for x in myresult] # decode bytearray
		return dict(zip(row_headers, result))
	else:
		return None

# Insert & Update
def inup(query, val, conn):
	mycursor = conn.cursor()
	mycursor.execute(query, val)
	conn.commit()

# Perintah Query Select ke JSON
def select(query, values, conn):
	mycursor = conn.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchall()
	json_data = []
	for result in myresult:
		json_data.append(dict(zip(row_headers, result)))
	return json_data

# Get single row
def select_row2(query, values, conn):
	mycursor = conn.cursor(buffered=True)
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchmany(1)
	json_data = []
	for result in myresult:
		json_data.append(dict(zip(row_headers, result)))
	return json_data

# Perintah Query Select ke JSON
def select_limit(query, values, conn, page=1):
	mycursor = conn.cursor()
	page = int(page)
	lim = 0
	off = 10
	if page == 1:
		lim = 0
	else: 
		lim = (page-1) * 10
	mycursor.execute(query + " limit "+str(lim)+", "+str(off) , values)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchall()
	json_data = []
	for result in myresult:
		json_data.append(dict(zip(row_headers, result)))
	return json_data

def select_limit_param(query, values, conn, page=1, off=10):
	mycursor = conn.cursor()
	page = int(page)
	lim = 0
	off = int(off)
	if page == 1:
		lim = 0
	else: 
		lim = (page-1) * off
	mycursor.execute(query + " limit "+str(lim)+", "+str(off) , values)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchall()
	json_data = []
	for result in myresult:
		json_data.append(dict(zip(row_headers, result)))
	return json_data

def select2(query, values, conn):
	mycursor = conn.cursor()
	mycursor.execute(query, values)
	myresult = mycursor.fetchall()
	return myresult

# Perintah Query Insert
def insert_lastrow(query, val, conn):
	mycursor = conn.cursor()
	mycursor.execute(query,val)
	conn.commit()

# Perintah Query Insert
def insert(query, val, conn):
	mycursor = conn.cursor()
	mycursor.execute(query,val)
	conn.commit()

# Perintah Query Insert
def insert2(query, val, conn):
	mycursor = conn.cursor()
	mycursor.execute(query,val)
	conn.commit()
	return mycursor.lastrowid

# Perintah Count
def row_count(query, conn):
	mycursor = conn.cursor()
	mycursor.execute(query)
	mycursor.fetchall()
	rc = mycursor.rowcount
	return rc

# Perintah eksekusi query tanpa values
def execute_sql(query, conn):
	mycursor = conn.cursor()
	mycursor.execute(query)
	row_headers = [x[0] for x in mycursor.description]
	myresult = mycursor.fetchall()
	json_data = []
	for result in myresult:
		json_data.append(dict(zip(row_headers, result)))
	return json_data


# Perintah Count plus filter
def row_count2(query, val,  conn):
	mycursor = conn.cursor()
	mycursor.execute(query, val)
	mycursor.fetchall()
	rc = mycursor.rowcount
	return rc