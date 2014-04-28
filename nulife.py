from flask import Flask, render_template, request, url_for, redirect, jsonify
import time
from flask_wtf import Form
from wtforms import TextField
from flask_wtf.html5 import IntegerField
import wolframalpha
import requests
import json
from parse import *
import codecs


app = Flask(__name__)
app.config.from_object('config')

@app.route('/testpoint', methods = ['POST'])
def testpoint():
	try:
		name = request.values['name']
		print name
	except KeyError:
		return "Something went wrong."
	return jsonify(name = name)

class nuForm(Form):
	zip_code = IntegerField('zip_code')
	salary = IntegerField('salary')


def remove(item):
	try:
		i1, i2 = item.split('(')
	except ValueError:
		return False
	i3, i4 = i2.split(',')
	i3 = float(i3)
	return i3


def zippo(zipcode):
	url = 'http://api.zippopotam.us/us/'
	zippo_call = url + "{}".format(zipcode)
	r = requests.get(zippo_call)
	j = r.json()
	state = j['places'][0]['state']
	state_abbr = j['places'][0]['state abbreviation']
	city = j['places'][0]['place name']

	return json.dumps({'city':city, "state":state, 'state_abbr':state_abbr})


def gasoline(city, state):
	client = wolframalpha.Client('QJTV48-7ETLWYVVE3')
	gas_query = 'gas ' + city + ', ' + state
	print gas_query
	res = client.query(gas_query)
	gas_raw = ()

	#gas_neat = search('${:f}/gal  (US dollars per gallon)  (Monday, April 21, 2014)',(next(res.results).text)).fixed


	gas_neat = search('$\\{:f}/\\gal  (US dollars per gallon)  (Monday, April 21, 2014)', gas_raw).fixed
	print gas_neat
	return True


def utilities(zipcode):
	pass

@app.route('/organize', methods = ['POST'])
def organize():
	salary = float(request.values['salary'])
	
	transportation = 0.00
	monthly_expenses = 0.00

	monthly_sal = salary / float(12)
	monthly_sal_af_tax = monthly_sal * .72
	monthly_savings = monthly_sal_af_tax * .15

	### Get city/state from zip or (if provided) just proceed
	try:
		zipcode = request.values['zipcode']
		citystate = zippo(zipcode)
		citystate = json.loads(citystate)
		city = citystate['city']
		state_abbr = citystate['state_abbr']

	except KeyError:
		city = request.values['city']
		state_abbr = request.values['state']

	print 'car stuff'
	### Car stuff
	try:
		cartype = request.values['cartype']
		insurance_year = float(request.values['insurance'])
		insurance = insurance_year / float(12)
		try:
			payments = float(request.values['payments'])
			monthly_expenses = payments

		except KeyError:
			payments = 0
			print "uh oh"

		car_month = car(float(cartype), payments, insurance)
		print "\nCar Month: ${}".format(car_month)
		transportation = car_month
		monthly_expenses = monthly_expenses + transportation

	except KeyError:
		transportation = float(request.values['trans'])
		monthly_expenses = monthly_expenses + transportation
		print monthly_expenses

	print 'phone stuff'
	### Cell phone stuff
	try:
		cell = float(request.values['cell'])
		monthly_expenses = monthly_expenses + cell
		print monthly_expenses
	except KeyError:
		pass

	print 'living expesnes'
	### Living expenses
	rent = float(request.values['rent'])
	nat = float(request.values['nat'])
	cable = float(request.values['cable'])
	gas = float(request.values['gas'])
	elec = float(request.values['elec'])
	groceries = float(request.values['groceries'])

	monthly_expenses = monthly_expenses + rent + nat + cable + gas + elec + groceries
	print monthly_expenses

	monthly_bal = monthly_sal_af_tax - monthly_savings - monthly_expenses

	return jsonify(monthly_bal = monthly_bal, transportation = transportation, monthly_sal_af_tax = monthly_sal_af_tax, monthly_savings = monthly_savings, monthly_expenses = monthly_expenses)

def car(type, payments, insurance):
	gas_price = app.config['US_GAS_AVG']
	cars = {1:10, 2:15, 3:20}
	tank = cars[type]
	gas_month = 2.00 * tank * gas_price
	car_total = gas_month + payments + insurance

	return car_total


def wolfram(city, state_abbr):
	client = wolframalpha.Client('QJTV48-7ETLWYVVE3')
	energy_query = 'utilities prices in ' + city + ' ' + state_abbr
	housing_query = 'fair market rent price ' + city + ' ' + state_abbr

	eres = client.query(energy_query)
	hres = client.query(housing_query)

	print (next(eres.results).text)
	print (next(hres.results).text)

	eraw = (next(eres.results).text)
	hraw = (next(hres.results).text)

	hneat = hraw.splitlines()

	housing_prices = []

	f = open('col_index2.json')
	d = f.read()
	data = json.loads(d)

	inc1 = 1

	for item in hneat:
		if inc1 == 5:
			break

		item = " " + str(item)
		regex = search('\\\\| ${:d} per month  (US dollars per month)', item)
		regex = remove(str(regex))

		if regex == False:
			ic = 0
			housing_sum = 0
			us_fmr = app.config['US_FMR']
			for item in data['results']['collection1']:
				shitty, abbr  = item['location'].split(', ')
				print abbr
				if abbr == state_abbr:
					housing_index = float(item['housing_index'])
					print housing_index
					housing_sum = housing_sum + housing_index

				ic = ic + 1
			housing_avg = housing_sum/ic
			print housing_avg
			housing_percent = housing_avg/100
			print housing_percent

			housing_prices = []

			for x in us_fmr:
				x = x * housing_percent
				print x
				housing_prices.append(x)



			final_data = {'energy_raw' : energy_raw, 'local_utilities' : local_utilities, 'local_milk' : local_milk, 'housing_prices' : housing_prices} 

			return final_data

		housing_prices.append(please2)
		incr = inc1 + 1

	final_data = {'energy_raw' : energy_raw, 'local_utilities' : local_utilities, 'local_milk' : local_milk, 'housing_prices' : housing_prices, 'hneat' : hneat}

	return final_data

def pubtrans():
	pass


def calculate(zip_code):

	user_state = state_abbr
	i = 0
	milk_summ = 0
	utility_summ = 0
	for item in data['results']['collection1']:
		shitty, abbr = item['location'].split(', ')
		if abbr == user_state:

			utility_index = float(item['utilities_index'])
			#print utility_index
			milk_index = float(item['grocery_index'])

			utility_summ = utility_summ + utility_index
			milk_summ = milk_summ + milk_index
			i += 1

	utility_avg = utility_summ/i
	#print utility_avg
	milk_avg = milk_summ/i

	milk_percent = milk_avg/100
	local_milk = float(base_milk) * milk_percent

	utility_percent = utility_avg/100
	local_utilities = float(base_util) * utility_percent

	local_milk = "{0:.2f}".format(local_milk)
	local_utilities = "{0:.2f}".format(local_utilities)

	#### Wolfram API Calls

	hous_neat = housing_raw.splitlines()

	print hous_neat

	housing_prices = []


	incr = 1

	for item in hous_neat:
		if incr == 6:
			break

		item2 = " " + str(item)
		please = search('\\\\| ${:d} per month  (US dollars per month)', item2)
		please2 = remove(str(please))

		if please2 == False:
			ic = 0
			housing_sum = 0
			us_fmr = app.config['US_FMR']
			for item in data['results']['collection1']:
				print item
				shitty, abbr  = item['location'].split(', ')
				print abbr
				if abbr == user_state:
					print user_state
					housing_index = float(item['housing_index'])
					print housing_index
					housing_sum = housing_sum + housing_index

				ic = ic + 1
				print ic
			housing_avg = housing_sum/ic
			print housing_avg
			housing_percent = housing_avg/100
			print housing_percent

			housing_prices = []

			for x in us_fmr:
				x = x * housing_percent
				print x
				housing_prices.append(x)



			final_data = {'energy_raw' : energy_raw, 'local_utilities' : local_utilities, 'local_milk' : local_milk, 'housing_prices' : housing_prices} 

			return final_data

		print please2
		housing_prices.append(please2)
		print incr
		incr = incr + 1


	print housing_prices



	#results(energy_final, local_utilities, local_milk)

	final_data = {'energy_raw' : energy_raw, 'local_utilities' : local_utilities, 'local_milk' : local_milk, 'housing_prices' : housing_prices}

	return final_data


@app.route('/liftoff', methods = ['POST'])
def liftOff(request):
	monthly_salary = salary/12
	sal_af_tax = monthly_salary * .72
	saved_monthly = sal_af_tax * .15
	gas_avg = app.config['US_GAS_AVG']
	avg_cable = 150
	month_bal = sal_af_tax - saved_monthly

	cars = {1:10, 2:15, 3:20}

	if carbool == True:

		tank = cars[cartype]
		gas_month = tank * 2 * gas_avg
		month_bal = month_bal - gas_month - insurance


		if paymentsbool == True:
			month_bal -= payments
			
	else:
		month_bal -= trans


	if cellbool == True:
		month_bal -= cell

	########### LIFTOFF ##########

	if lifechoice == True:

		avg_groceries = app.config['AVG_GROCERIES']
		month_bal -= avg_groceries
		data = calculate(zipcode)	

		housing = data['housing_prices']

		i = 0
		avg_house = 0

		for x in housing:
			avg_house += x
			i += 1

		avg_house = avg_house/i

		energy = data['energy_raw']
		elect = search('electricity price \\| {:f}', energy).fixed
		natura = search('natural gas price \\| ${:f} per', energy).fixed

		#hous_neat = hous_raw.splitlines()
		
		elec = " " + str(elect)
		elec = float(remove(elec))

		natural = " " + str(natura)
		natural = float(remove(natural))

		milk = float(data['local_milk'])
		utilities = float(data['local_utilities'])

		month_bal = month_bal - float(utilities)

		return json.dumps({'milk':milk, 'utilities':utilities, 'natural':natural, 'elec':elec, 'sal_af_tax':sal_af_tax, 'saved_monthly':saved_monthly, 'month_bal':month_bal})


		########### GET ORGANIZED ##########

	else:
		
		month_bal -= groceries
		month_bal = month_bal - elec - nat - gas

		return jsonify(milk = milk, sal_af_tax = sal_af_tax, saved_monthly = saved_monthly, month_bal = month_bal)


@app.route('/', methods = ['GET', 'POST'])
def index():
	form = nuForm()
	if request.method == 'POST':
		print "\nFORM IS VALID"
		zip_code = request.form['zip_code']
		salary = request.form['salary']
		print salary
		data = calculate(zip_code)
		energy = data['energy_raw']
		
		#hous_raw = data['housing_raw']
		
		elec = search('electricity price \\| {:f}', energy).fixed
		nat = search('natural gas price \\| ${:f} per', energy).fixed

		#hous_neat = hous_raw.splitlines()
		
		elec = " " + str(elec)
		elec = remove(elec)
		nat = " " + str(nat)
		nat = remove(nat)
		milk = data['local_milk']
		utilities = data['local_utilities']

		return render_template('results.html', elec = elec, milk = milk, utilities = utilities, nat = nat )

	else:

		return render_template('index.html', form = form)





@app.route('/results', methods = ['GET'])
def results(energy, utilities, milk):
	print "\nSTARTING RESULTS"
	return render_template('results.html', energy=energy)





if __name__ == '__main__':
	app.run(host="0.0.0.0", port=8080)
