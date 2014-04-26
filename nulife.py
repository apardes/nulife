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


@app.route('/results', methods = ['GET'])
def results(energy, utilities, milk):
	print "\nSTARTING RESULTS"
	return render_template('results.html', energy=energy)


def calculate(zip_code, salary):

	print "\nSTARTING CALCULATIONS"
	base_milk = 4.16
	print base_milk
	base_util = 159.22
	avg_groceries = 294.34

	#### Getting City/State from ZIP

	zippo = 'http://api.zippopotam.us/us/'
	zip_call = zippo + zip_code 
	print zip_call
	r = requests.get(zip_call)
	j = r.json()

	state = j['places'][0]['state']
	state_abbr = j['places'][0]['state abbreviation']
	city = j['places'][0]['place name']
	print city

	#### Calculating local Milk and Utility Costs

	f = open('col_index.json')
	d = f.read()
	data = json.loads(d)

	user_state = state_abbr
	i = 0
	milk_summ = 0
	utility_summ = 0
	for item in data['results']['collection1']:
		shitty, abbr = item['location'].split(', ')
		if abbr == user_state:

			utility_index = float(item['utility_index'])
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
	print energy_query
	res = client.query(energy_query)



	print(next(res.results).text)


	energy_final = (next(res.results).text)


	#results(energy_final, local_utilities, local_milk)

	final_data = {'energy_final' : energy_final, 'local_utilities' : local_utilities, 'local_milk' : local_milk}

	return final_data


def remove(item):
	i1, i2 = item.split('(')
	i3, i4 = i2.split(',')
	return i3


@app.route('/', methods = ['GET', 'POST'])
def index():
	form = nuForm()
	if request.method == 'POST':
		print "\nFORM IS VALID"
		zip_code = request.form['zip_code']
		salary = request.form['salary']
		print salary
		data = calculate(zip_code, salary)
		print data

		energy = data['energy_final']
		elec = search('electricity price \\| {:f}', energy).fixed
		nat = search('natural gas price \\| ${:f} per', energy).fixed
		
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
