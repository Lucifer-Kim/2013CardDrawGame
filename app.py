#Create by Minji Yang
# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, redirect, request, flash
from mongokit import Connection, Document
from bson.objectid import ObjectId
import random

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT =	27017
SECRET_KEY = 'a@awf!@#!@!@'

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection(app.config['MONGODB_HOST'],
						app.config['MONGODB_PORT'])

levels = [u'S', u'A', u'B', u'C', u'D']
rates = [1, 10, 100, 400, 1000]

# S 1000 / 900-1000
# A 100 / 70-100
# B 40 / 35-40
# C 25 / 20-25
# D 15 / 1-15
powerRan = [
	(900, 1000), (70, 100), (35, 40), (20, 25), (1, 15)
]

class Card(Document):
	"""Card Information
	 - 'level' is.. S,A,B,C,D
	 - 'levelCode' is.. 0 to 4
	 - 'strength' is.. card's strength
	""" 
	structure = {
		'level' : unicode,
		'levelCode' : int,
		'strength' : int
	}

	use_dot_notation = True

	def __repr__(self):
		return 'level: %s, strength: %s'%(self.level, self.strength)

connection.register([Card])

collection = connection['test'].users

@app.route('/')
def index():
	"""Card List 
	"""
	cards = list(collection.Card.find())
	total = {}
	for card in cards:
		level = card.level
		if total.get(level) is None:
			total[level] = {
				'level': card.level,
				'count': 1, 'strength': card.strength
			}
		else:
			total[level] = {
				'level': card.level,
				'count': total[level]['count'] + 1,
				'strength': total[level]['strength'] + card.strength
			}

	return render_template('index.html',
		cards = cards, total = total)


def generateStr(level):
	"""Generate strength by level
	"""
	start, end = powerRan[level]
	return random.randrange(start, end)

def drawCard():
	"""Draw Card
	- Generate card by probability
	"""
	level = None
	value = random.randrange(0, 1000)
	for i in range(0, len(rates)):
		rate = rates[i]
		if value < rate:
			level = i
			break
	return (level, generateStr(level))

@app.route('/compose')
def compose():
	ids = request.args.getlist('cardId')
	cards = []
	for id in ids:
		cards.append(collection.Card.get_from_id(ObjectId(id)))
	card1, card2 = cards
	level = card1.levelCode - 1
	if card1.levelCode != 0 and card1.level == card2.level:
		# card level is same.
		for card in cards:
			card.delete()
		card = collection.Card()
		card['levelCode'], card['strength'] = level, generateStr(level)
		card['level'] = levels[card['levelCode']]
		card.save()
		return render_template('compose.html', card=card)
	else:
		if card1.levelCode == 0:
			flash('Sorry, S is not support.')
		elif card1.level != card2.level:
			flash('Sorry, You have to choose same level.')
		else:
			flash('Sorry, You have to choose only two.')
		return redirect('/')

@app.route('/remove')
def remove():
	"""Remove card
	"""
	id = request.args.get('id')
	if id:
		collection.Card.get_from_id(ObjectId(id)).delete()
	return redirect('/')

@app.route('/draw', methods=['GET','POST'])
def draw():
	if request.method == 'POST':
		# draw and show card  
		card = collection.Card()
		card['levelCode'], card['strength'] = drawCard()
		card['level'] = levels[card['levelCode']]
		card.save()
		return render_template('draw.html', card = card)
	else:
		return render_template('draw.html')

@app.route('/clear')
def clear():
	"""Clear all card 
	"""
	collection.remove()
	return redirect('/')

app.run(debug=True)
