from flask import Flask, request
import urllib.request
import json

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


app = Flask(__name__)

def isLoggedIn(req):
	json_data =  json.loads (req.data)
	user = json_data['user']
	return  'idToken' in user

def getUserDetails(req):
	json_data =  json.loads (req.data)
	idToken = json_data['user']['idToken']
	url = 'https://oauth2.googleapis.com/tokeninfo?id_token='+idToken
	f = urllib.request.urlopen(url)
	user_json = json.loads(f.read().decode('utf-8'))

	return user_json['given_name'], user_json['email']




def getIntent(req):
	json_data =  json.loads (req.data)
	logging.info('JSON Data =' + str(json_data))
	intent = json_data['inputs'][0]['intent']
	return intent

def getQuery(req):
	json_data =  json.loads(req.data)
	logging.info('JSON Data =' + str(json_data))
	query = json_data['inputs'][0]['rawInputs'][0]['query']
	return  query

def getCancleIntentJson():
	json_str = '''{
		  "expectUserResponse": false,
		  "finalResponse": {
			"richResponse": {
			  "items": [
				{
				  "simpleResponse": {
					"textToSpeech": "Good bye"
				  }
				}
			  ]
			}
		  }
		}'''
	return json_str

def getSigninIntentJson():
	json_str = '''{
		  "expectUserResponse": true,
		  "expectedInputs": [
		    {
		      "inputPrompt": {
		        "richInitialPrompt": {
		          "items": [
		            {
		              "simpleResponse": {
		                "textToSpeech": "Please signin"
		              }
		            }
		          ]
		        }
		      },
		      "possibleIntents": [
		        {
		          "intent": "actions.intent.SIGN_IN",
		          "inputValueData": {
		            "@type": "type.googleapis.com/google.actions.v2.SignInValueSpec"
		          }
		        }
		      ]
		    }
		  ],
		  
		}'''
	return json_str


def getMainIntentJson(name):
	json_str = '''{
	  "expectUserResponse": true,
	  "expectedInputs": [
	    {
	      "possibleIntents": [
	        {
	          "intent": "actions.intent.TEXT"
	        }
	      ],
	      "inputPrompt": {
	        "richInitialPrompt": {
	          "items": [
	            {
	              "simpleResponse": {
	                "textToSpeech": "Hi %s, I am your assistant"
	              }
	            }
	          ]
	        }
	      }
	    }
	  ]
	}''' % (name)
	return json_str


def getTextIntentJson():
	json_str = '''{
	  "expectUserResponse": true,
	  "expectedInputs": [
	    {
	      "possibleIntents": [
	        {
	          "intent": "actions.intent.TEXT"
	        }
	      ],
	      "inputPrompt": {
	        "richInitialPrompt": {
	          "items": [
	            {
	              "simpleResponse": {
	                "textToSpeech": "This is query response"
	              }
	            }
	          ]
	        }
	      }
	    }
	  ]
	}'''
	return json_str

def getSignInStatus(req):
	json_data =  json.loads(req.data)
	logging.info('JSON Data =' + str(json_data))
	status = json_data['inputs'][0]['arguments'][0]['extension']['status']
	return  status



@app.route('/query',methods = ['POST'])
def hello():
	
	intent=  getIntent(request)
	
	logging.info('Intent = '+ intent)
	#logging.info('Query = '+ query)

	if intent == 'actions.intent.CANCEL':
		return getCancleIntentJson()

	elif intent == 'actions.intent.MAIN':
		if not isLoggedIn(request):
			return getSigninIntentJson()
		else:
			name, _ = getUserDetails(request)
			logging.info('Logged in user is :'+ name)
			return getMainIntentJson(name)


	elif intent == 'actions.intent.TEXT':
		if not isLoggedIn(request):
			return getSigninIntentJson()
		else:
			getUserDetails(request)
			return getTextIntentJson()

	elif intent == 'actions.intent.SIGN_IN':
		status = getSignInStatus(request)
		print('Login status = '+ status)
		name, _ = getUserDetails(request)
		logging.info('Logged in user is :'+ name)
		return getMainIntentJson(name)


if __name__ == '__main__':
	app.run()