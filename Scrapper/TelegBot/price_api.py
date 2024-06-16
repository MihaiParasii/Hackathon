import requests, json

DEFAULT_URL = "http://localhost:5000/api"
AUTH_TOKEN_ARR = []


def authentificate():
    auth_data = {
    'username': 'user3',
    'password': 'user3',
    'rememberMe': False
    }

    auth_json_data = json.dumps(auth_data)

    headers = {'Content-Type': 'application/json'}

    response = requests.post(DEFAULT_URL + "/authenticate", data=auth_json_data, headers=headers)
    if response.status_code == 200:
        print('POST request was successful!')
        # Parse the JSON response
        response_data = response.json()
        print('Response data:', response_data)
        # Access the 'id_token' from the response
        id_token = response_data.get('token', '')
        print('ID Token:', id_token)
        AUTH_TOKEN_ARR.clear()
        AUTH_TOKEN_ARR.append(id_token)
    else:
        print('POST request failed with status code:', response.status_code)

def get_prices(user):
    AUTH_TOKEN = AUTH_TOKEN_ARR[0]
   
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }
    response = requests.get(DEFAULT_URL + "/prices/query/" + str(user.id) , headers=headers)
    if response.status_code == 200:
        print('GET request was successful!')
        # Parse the JSON response
        response_data = response.json()
        product_list = response_data
        links_and_discs = [{"link": product['link'], "disc": product['disc']} for product in product_list]
        return links_and_discs
    else:
        print('POST request failed with status code:', response.status_code)
        return None
    
def getCategories():
    AUTH_TOKEN = AUTH_TOKEN_ARR[0]

    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }
    response = requests.get(DEFAULT_URL + "/filter/categories", headers=headers)
    if response.status_code == 200:
        print('GET request was successful!')
        # Parse the JSON response
        response_data = response.json()
        product_list = response_data
        return product_list 
    else:
        print('POST request failed with status code:', response.status_code)
        return []
    
def select_preferences(user_prefs):
    AUTH_TOKEN = AUTH_TOKEN_ARR[0]
    user_prefs_json = json.dumps(user_prefs.__dict__)

    headers = {'Content-Type': 'application/json',
                'Authorization': f'Bearer {AUTH_TOKEN}'
               }

    response = requests.post(DEFAULT_URL + "/preferences", data=user_prefs_json, headers=headers)
    if response.status_code == 200:
        print('POST request was successful!')
        return user_prefs
    else:
        print('POST request was unsucceseful!')
        return None


def getBrandsByCategory(category):
    AUTH_TOKEN = AUTH_TOKEN_ARR[0]

    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }
    url = DEFAULT_URL + "/filter/category/" + category + "/brands"
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('GET request was successful!')
        # Parse the JSON response
        response_data = response.json()
        product_list = response_data
        return product_list 
    else:
        print('Get request failed with status code:', response.status_code)
        return []
        
    
