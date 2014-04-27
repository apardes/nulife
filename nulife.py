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


def gasoline(city, state):
	client = wolframalpha.Client('QJTV48-7ETLWYVVE3')
	gas_query = 'gas ' + city + ', ' + state
	print gas_query

	res = client.query(gas_query)

	
	gas_neat = search('${:f}/gal  (US dollars per gallon)  (Monday, April 21, 2014)',(next(res.results).text)).fixed


	gas_neat = search('${:f}/gal  (US dollars per gallon)  (Monday, April 21, 2014)', gas_raw).fixed

	print gas_neat

	return True


@app.route('/results', methods = ['GET'])
def results(energy, utilities, milk):
	print "\nSTARTING RESULTS"
	return render_template('results.html', energy=energy)


def calculate(zip_code):

	print "\nSTARTING CALCULATIONS"
	base_milk = 4.16
	print base_milk
	base_util = 159.22
	avg_groceries = 294.34

	#### Getting City/State from ZIP
	print zip_code
	zippo = 'http://api.zippopotam.us/us/'
	zip_call = zippo + "{}".format(zip_code)
	print zip_call
	r = requests.get(zip_call)
	j = r.json()
	print j
	state = j['places'][0]['state']
	print state
	state_abbr = j['places'][0]['state abbreviation']
	city = j['places'][0]['place name']
	print city

	#### Calculating local Milk and Utility Costs

	f = open('col_index2.json')
	d = f.read()
	data = json.loads(d)

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

	client = wolframalpha.Client('QJTV48-7ETLWYVVE3')
	energy_query = 'utilities prices in ' + city + ' ' + state_abbr
	housing_query = 'fair market rent price ' + city + ' ' + state_abbr
	print energy_query
	print housing_query
	res = client.query(energy_query)
	hres = client.query(housing_query)



	#print(next(res.results).text)
	#print(next(hres.results).text)


	energy_raw = (next(res.results).text)
	housing_raw = (next(hres.results).text)

	print housing_raw

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
					print "wtf"
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
def liftOff(lifechoice, zipcode, salary, carbool, trans, paymentsbool, cartype, payments, insurance, cellbool, cell, rent, nat, cable, gas, groceries, elec):
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


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=8080)
