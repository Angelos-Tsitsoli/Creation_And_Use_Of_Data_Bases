# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys, os

sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db


def connection():
	''' User this function to create your connections '''
	con = db.connect(
		settings.mysql_host,
		settings.mysql_user,
		settings.mysql_passwd,
		settings.mysql_schema)

	return con


def findAirlinebyAge(x, y):
	try:
		int(x)
		int(y)
	except:
		return [("Error x and y must be integers",)]

	# Create a new connection
	con = connection()
	# Create a cursor on the connection
	cur = con.cursor()
	sql = f"""select airlines.id,airlines.name ,count(flights_has_passengers.passengers_id) 
				from flights_has_passengers,flights,routes,airlines
				where  flights_has_passengers.flights_id=flights.id and flights.routes_id=routes.id 
					and routes.airlines_id = airlines.id and flights_has_passengers.passengers_id 
					in (select passengers.id
						from passengers
						where (2022-passengers.year_of_birth)>%d and (2022-passengers.year_of_birth)< %d
					) 
				group by(airlines.id)
				order by  (count(flights_has_passengers.passengers_id) ) desc""" % (int(y), int(x))
	cur.execute(sql)

	(airlines_id, airlines_name, num_of_passengers) = cur.fetchone()

	sql = f"""select count(airlines_has_airplanes.airplanes_id) 
				from airlines_has_airplanes
				where airlines_has_airplanes.airlines_id = %d """ % int(airlines_id)
	cur.execute(sql)
	num_of_airplanes = cur.fetchone()
	num_of_airplanes = num_of_airplanes[0]
	return [("airlines_name", "num_of_passengers", "num_of_airplanes")] + [
		(airlines_name, num_of_passengers, num_of_airplanes)]


def findAirportVisitors(x, a, b):
	# Create a new connection
	con = connection()
	# Create a cursor on the connection
	cur = con.cursor()

	sql = """
			select airports.name,count(flights_has_passengers.passengers_id)
			from airports,routes,airlines,flights,flights_has_passengers
			where flights_has_passengers.flights_id = flights.id and flights.routes_id = routes.id and routes.airlines_id = airlines.id  and routes.destination_id = airports.id 
			and airlines.name = "%s" and flights.date > "%s" and flights.date < "%s"
			group by(airports.id)
			order by(count(flights_has_passengers.passengers_id)) desc
			""" % (x, a, b)

	cur.execute(sql)
	tuples = list(cur.fetchall())

	return [("airport_name", "number_of_visitors")] + tuples  # [list1[:][0],list1[:][1]]


def findFlights(x, a, b):
	# Create a new connection
	con = connection()
	# Create a cursor on the connection
	cur = con.cursor()

	sql = """select flights.id ,airlines.alias ,air2.name , airplanes.model
			from flights,routes,airports air1,airports air2 ,airlines,airplanes 
			where flights.routes_id=routes.id and routes.source_id=air1.id and routes.destination_id=air2.id and
			 air1.city= "%s" and air2.city= "%s" and 
			 routes.airlines_id=airlines.id and airlines.active='Y' and 
			 flights.date= "%s" and flights.airplanes_id=airplanes.id 
			group by(flights.id)""" % (a, b, x)

	cur.execute(sql)
	tuples = list(cur.fetchall())

	# print(tuples)

	# flight_id = []
	# alt_name = []
	# dest_name = []
	# aircraft_model = []

	# for x in tuples:

	#	flight_id.append(x[0])
	#	alt_name.append(x[1])
	#	dest_name.append(x[2])
	#	aircraft_model.append(x[3])

	return [("flight_id", "alt_name", "dest_name", "aircraft_model")] + tuples


def findLargestAirlines(N):
	try:
		N = int(N)

	except:
		return [("Error N must be an integer",)]

	# Create a new connection
	con = connection()

	# Create a cursor on the connection
	cur = con.cursor()


	sql = """   select airlines.id,airlines.name,airlines.code,count(flights.id)
				from airlines,routes,flights
				where flights.routes_id=routes.id and routes.airlines_id=airlines.id
				group by(airlines.id)
				order by  (count(flights.id) ) desc"""

	cur.execute(sql)

	unique_id = []
	array_of_tuples = []

	for i in range(N):
		list_tuple = list(cur.fetchone())
		array_of_tuples.append(list_tuple)
		unique_id.append(list_tuple[0])

	#Holds N airlines with most flights

	tuple_after_N = list(cur.fetchone())

	while (list_tuple[3] == tuple_after_N[3]):	#Adds every airline with same num of flights as the N-th
		array_of_tuples.append(tuple_after_N)
		unique_id.append(tuple_after_N[0])
		tuple_after_N = list(cur.fetchone())

	num_of_aircrafts = []

	for u_id in unique_id:
		sql = """   select  count(airlines_has_airplanes.airplanes_id)
						from airlines_has_airplanes
						where airlines_has_airplanes.airlines_id = %d
						""" % int(u_id)
		cur.execute(sql)
		tupl = cur.fetchone()
		num_of_aircrafts.append(tupl[0])

	for i in range(len(num_of_aircrafts)):
		del array_of_tuples[i][0]
		array_of_tuples[i].append(num_of_aircrafts[i])
		array_of_tuples[i] = tuple(array_of_tuples[i])

	return [("name", "id", "num_of_flights", "num_of_aircrafts")] + array_of_tuples


def insertNewRoute(x, y):
	# Create a new connection
	con = connection()

	# Create a cursor on the connection
	cur = con.cursor()
	######################################################
	# sql = "delete  from routes r where r.id = 67663;"
	# cur.execute(sql)
	# 													# in order to delete the first two new tuples which will have been inserted
	# sql = "delete  from routes r where r.id = 67664;"
	# cur.execute(sql)
	##########################################################3

	# get airlines.id
	sql = """	select airlines.id
				from airlines
				where airlines.alias = "%s"	""" % x

	cur.execute(sql)
	airlines_id = cur.fetchone()
	airlines_id = int(airlines_id[0])

	# get source_id
	sql = """	select airports.id
				from airports
				where airports.name= "%s" """ % y

	cur.execute(sql)
	air_source_id = cur.fetchone()
	air_source_id = int(air_source_id[0])

	# get dest_id
	sql = """select distinct air1.id
			from airports air1
			where air1.city not in(
			select  distinct air2.city
			from airports air2,airports air3,routes,airlines
			where  airlines.id = %d and airlines.id = routes.airlines_id and routes.destination_id = air2.id and
			routes.source_id = air3.id and air3.id = %d )  """ % (airlines_id, air_source_id)

	cur.execute(sql)
	dest_id = cur.fetchone()
	dest_id = int(dest_id[0])

	if (dest_id != None):
		sql = "select max(r.id) from routes r"
		cur.execute(sql)

		max_id = cur.fetchone()
		max_id = int(max_id[0])

		# print(max_id) #see the current max_id

		max_id += 1  # create a new id

		sql = "insert into routes(id,airlines_id,source_id,destination_id) values (%d,%d,%d,%d);" % (
			max_id, airlines_id, air_source_id, dest_id)

		cur.execute(sql)

		####################################
		# sql = "select max(r.id) from routes r"
		# cur.execute(sql)
		# print(cur.fetchone())	#in order to see the new max_id in the DB
		# sql = "delete  from routes r where r.id = %d;" % max_id		#in order to immediately delete the tuple,that has just been inserted
		# cur.execute(sql)
		#####################
		return ("OK")

	else:
		return ("airline capacity full")

# prints to test the functionality of the code written above
# print(findAirlinebyAge(20,50))
# print(findAirportVisitors('Aegean Airlines','2010-03-01','2022-07-17'))
# print(findFlights('2014-11-03','Male','Dubai'))
# print(findLargestAirlines(5))
# print(insertNewRoute('Emirates Airlines','Dubai Intl'))

# check: if max_id = 67662
# ===> Means(if changes have not been made in the DB) no new tuple has been inserted in the initial DB
# ===> You can use the deletions of the max_id above and the code below to check if the added tuple has been deleted

# con = connection()
# cur = con.cursor()
# sql = "select max(r.id) from routes r"
# cur.execute(sql)
# max_id = cur.fetchone()
# max_id = int(max_id[0])
# print(max_id) #see the current max_id