with open("policy.txt", "r") as f:
	lines = [line.rstrip() for line in f]

l = []
for i in lines:
	x = i.split(',')
	m = {}
	for j in x:
		if('=' in j):
			k = j.split('=')
			m[k[0]] = True if k[1] == "True" else False
		m['action'] = j
	l.append(m)



import re

# holding the static values
food = ["italian", "chinese", "japanese", "mexican", "greek", "any"]
cheap = ["cheap", "medium-priced", "expensive", "any"]
locs = ["marina del rey", "venice" , "santa monica" , "korea town" ,
"playa vista" , "hollywood", "any"]


############## Data Nodes
# objects to store slot info
objs = {
	"food": {
		"value": None,
		"arr": [(food, "food"), (cheap, "cheap"),(locs, "locs")],
		"confirmed": False,
		"templateAsk": "What type of food do you want?\n Your answer: ",
		"templateConfirm": "Ok you said you wanted a %s restaurant, right?\n Your answer: "
	},
	"cheap": {
		"value": None,
		"confirmed": False,
		"arr": [(cheap, "cheap"),(locs, "locs"), (food, "food")],
		"templateAsk": "How expensive a restaurant do you want?\n Your answer: ",
		"templateConfirm": "Ok you said you wanted a %s restaurant, right?\n Your answer: "
	},
	"locs": {
		"value": None,
		"confirmed": False,
		"arr": [(locs, "locs"), (food, "food"), (cheap, "cheap")],
		"templateAsk": "Ok where do you want the restaurant to be located?\n Your answer: ",
		"templateConfirm": "Ok you said you wanted a restaurant in %s, right?\n Your answer: "
	}
}

######################## Functional Nodes

# Handle getting items from the string input
def getItems(inp, arr):

	# iterates thru the array in correct order
	inp = inp.lower()
	for i in arr:
		ignoreAny = False
		for j in i[0]:
			if j in inp:
				if(j == "any" and ignoreAny): continue
				objs[i[1]]["value"] = j
				objs[i[1]]["confirmed"] = False
				ignoreAny = True
				endIdx = inp.find(j, 0);
				while((inp.find("any", 0, endIdx)) != -1):
					tmp = (inp.find("any", 0, endIdx))
					if(tmp == 0):
						inp = inp[3:]
					else:
						inp = inp[0:tmp-1] + inp[tmp:]
				inp = inp.replace(j, "", 1)

def serialize():
	mapping = {
	'food' : 'FOOD_TYPE',
	'cheap': 'PRICE',
	'locs': 'LOCATION'
	}
	state = {}
	for i in objs:
		prefix = mapping[i] 
		suffix = ''
		if objs[i]['value'] != None:
			state[prefix + '_FILLED'] = True
		else:
			state[prefix + '_FILLED'] = False

		if objs[i]['confirmed']:
			state[prefix + '_CONF'] = True
		else:
			state[prefix + '_CONF'] = False
	return state


# ask function for ask nodes
def ask(t):
	x = input(objs[t]["templateAsk"])
	getItems(x, objs[t]["arr"])
	return serialize()

# confirmation function for confirm nodes
def confirm(t):
	if(objs[t]["confirmed"] or len(objs[t]["value"]) == 0):
		return serialize()
	c = input(objs[t]["templateConfirm"] % objs[t]["value"])
	if("no" in re.sub('[\W\_]',' ',c).lower().split()):
		objs[t]["value"] = ""
		getItems(c, objs[t]["arr"])
	elif("yes" in re.sub('[\W\_]',' ',c).lower().split()):
		objs[t]["confirmed"] = True
		getItems(c, objs[t]["arr"])
	else:
		getItems(c, objs[t]["arr"])
	return serialize()


def act(state):

	action = ''
	for i in l:
		flag = False
		k = i.copy()
		del k['action']
		if(k == state):
			action = i['action']
			break


	if(action == "REQUEST_FOOD_TYPE"):
		return ask('food')
	if(action == "REQUEST_PRICE"):
		return ask('cheap')
	if(action == "REQUEST_LOCATION"):
		return ask('locs')
	if(action == "EXPLICIT_CONFIRM_FOOD_TYPE"):
		return confirm('food')
	if(action == "EXPLICIT_CONFIRM_PRICE"):
		return confirm('cheap')
	if(action == "EXPLICIT_CONFIRM_LOCATION"):
		return confirm('locs')
	



while(True):
	state = act(serialize())
	isDone = all(state.values())
	if(isDone):
		break






# read db
inputtext = open('restaurantDatabase.txt', 'r+')
inputtext1 = inputtext.readlines()

# construct matching items list
items = []
for i in inputtext1:
	if(i == "RESTAURANT_NAME	RESTAURANT_PHONE_NUMBER	FOOD_TYPE	PRICE	LOCATION\n"):
		continue
	tmp = i.lower().split("\t")
	if((tmp[2] == objs["food"]["value"] or objs["food"]["value"] == "any") and (tmp[3] == objs["cheap"]["value"] or objs["cheap"]["value"] == "any" ) and (tmp[4].strip() == objs["locs"]["value"].strip() or objs["locs"]["value"] == "any")):
		items.append(i)

# build formatted string and print it
formattedHead = "I found %i restaurants matching your query. " % len(items)
formattedRestaurant = "%s is an %s %s restaurant in %s. The phone number is %s. "
out = formattedHead
for i in items:
	tmp = i.split("\t")
	out += formattedRestaurant % (tmp[0].strip(), tmp[3].strip(), tmp[2].strip(), tmp[4].strip(), tmp[1].strip())
print(out)
