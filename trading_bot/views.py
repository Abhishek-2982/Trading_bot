# from django.http import HttpResponse
import json
from django.shortcuts import render, redirect
from .forms import KlineForm,BybitDataForm
from pybit.unified_trading import HTTP
from django.contrib.auth import get_user_model, login
import time, requests
import pandas as pd
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import login
from .forms import TAAPIForm,OrderForm,ApiForm
from .keys import api,secret
import hmac
import hashlib
import datetime
from delta_rest_client import DeltaRestClient


def homepage(request):
    # return HttpResponse("hey ! I'm home")
    return render(request,'home.html')

def mainpage(request):
   return render(request,'index.html')

def about(request):
    # return HttpResponse("My about")
    return render(request,'about.html')

def kline_view(request):

    if request.method == 'POST':
        form = KlineForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            current_time_millis = int(time.time() * 1000)  # Get current time in milliseconds

# Since current time is after the provided range, set start and end accordingly
            start = current_time_millis - 1000 *60 *60  # 1 hour before current time
            end = current_time_millis  
            # Integrate error handling for Pybit API calls
            try:
                session = HTTP(testnet=True)
                response = session.get_kline(
                    category=category,
                    symbol=symbol,
                    interval=interval,
                    start=start,  # Convert to seconds
                    end=end
                )
                # Process and display the response data here (e.g., using templates)
                context = {'response': response}
                return render(request, 'kline_response.html', context)
            except Exception as e:
                context = {'form': form, 'error': f'Error fetching data: {e}'}
                return render(request, 'kline_form.html', context)
    else:
        form = KlineForm()
    context = {'form': form}
    return render(request, 'kline_form.html', context)
  
def bybit_data_view(request):
 if request.user.is_authenticated:

  if request.method == 'POST':
    form = BybitDataForm(request.POST)
    if form.is_valid():
      # Extract data from the form, including category
      parameters = form.cleaned_data

      # Bybit API interaction (assuming testnet)
      session = HTTP(testnet=True)  # Change to False for mainnet

      # Get server time
      server_time_response = session.get_server_time()
      server_time = server_time_response['result']['timeSecond']

      # Calculate current timestamp and hours ago timestamp
      current_timestamp = int(server_time)
      hours_ago = (parameters['limit'] * parameters['interval']) / 60

      # Fetch K-line and premium index data
      kline_response = session.get_kline(
          category=parameters['category'],  # Use form data for category
          symbol=parameters['symbol'],
          interval=parameters['interval'],
          start=current_timestamp - (hours_ago * 3600),  # Convert to milliseconds
          end=current_timestamp * 1000,  # Convert to milliseconds
          limit=parameters['limit']
      )
      premium_index_response = session.get_premium_index_price_kline(
          category=parameters['category'],  # Use form data for category
          symbol=parameters['symbol'] + "T",  # Append "T" for premium index
          interval=parameters['interval'],
          start=current_timestamp - (hours_ago * 3600),  # Convert to milliseconds
          end=current_timestamp * 1000,  # Convert to milliseconds
          limit=parameters['limit']
      )

      # Prepare response data
      response_data = {
          "server_time": server_time_response,
          "kline_data": kline_response['result']['list'],
          "premium_index_data": premium_index_response['result']['list']
      }

      return JsonResponse(response_data)  # Return JSON response
  else:
    form = BybitDataForm()
  return render(request, 'bybit_data_form.html', {'form': form})
 else:
    return redirect('login')

def register_view(request):
    if request.method == "POST": 
        form = UserCreationForm(request.POST) 
        if form.is_valid(): 
            login(request, form.save())
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "register.html", { "form": form })

def login_view(request): 
    if request.method == "POST": 
        form = AuthenticationForm(data=request.POST)
        if form.is_valid(): 
            login(request, form.get_user())
            return redirect("homepage")
    else: 
        form = AuthenticationForm()
    return render(request, "login.html", { "form": form })

def logout(request):
  logout(request)
  return redirect('login') 

def taapi_form(request):
    if request.method == 'POST':
        form = TAAPIForm(request.POST)
        if form.is_valid():
            # Get form data
            exchange = form.cleaned_data['exchange']
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            indicators = form.cleaned_data['indicators']

            # Construct API payload
            payload = {
                "secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjYzZTUzMzBmNWFmOTRlZWNlNzFiODgzIiwiaWF0IjoxNzE1MzYwNjA0LCJleHAiOjMzMjE5ODI0NjA0fQ.B132F5h9XA-94vhHtS_Ky7Z9kfxVnDOI5QUOod1Od_0",
                "construct": {
                    "exchange": exchange,
                    "symbol": symbol,
                    "interval": interval,
                    "indicators": [{"indicator": ind.split('_')[0], "period": int(ind.split('_')[1])} for ind in indicators]
                }
            }

            # Make API request
            response = requests.post("https://api.taapi.io/bulk", json=payload)
            data = response.json()

            return render(request, 'weblivedata.html', {'data': data})

    else:
        form = TAAPIForm()

    return render(request, 'taapi_form.html', {'form': form})

def fetch_taapi_data(request):
    # Function to fetch TAAPI data
    # This function will be called via AJAX every 17 seconds
    # Construct the payload
    payload = {
        "secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjYzZTUzMzBmNWFmOTRlZWNlNzFiODgzIiwiaWF0IjoxNzE1MzYwNjA0LCJleHAiOjMzMjE5ODI0NjA0fQ.B132F5h9XA-94vhHtS_Ky7Z9kfxVnDOI5QUOod1Od_0",
        "construct": {
            # Use your desired parameters here
            "exchange": "binance",
            "symbol": "BTC/USDT",
            "interval": "5m",
            "indicators": [{"indicator": "ma", "period": 50}, {"indicator": "ma", "period": 200}]
        }
    }

    # Make API request
    response = requests.post("https://api.taapi.io/bulk", json=payload)
    data = response.json()

    return JsonResponse(data)

# set order form views function 
def place_order(request):
    if request.method == 'POST':
        # Accessing form data sent via AJAX request
        category = request.POST.get('category')
        symbol = request.POST.get('symbol')
        order_type = request.POST.get('orderType')
        # Extract other form data properties as needed
        amount = request.POST.get('price')
        time_in_force = request.POST.get('timeInForce')
        order_link_id = request.POST.get('orderLinkId')
        is_leverage = request.POST.get('isLeverage')
        order_filter = request.POST.get('orderFilter')
        # Calculate qty if needed
        # kline=get_kline_data(symbol,'1h',limit=1)
        # current_price = float(kline[0][4])
        # print(current_price)
        current_price=61600
        qty_str = amount / current_price
        qty = str(qty_str)
        # print(qty)
            # Place an order
        session = HTTP(testnet=True, api_key=api, api_secret=secret)
        response = session.place_order(
                category=category,
                symbol=symbol,
                side="Buy",  # You can set the side based on your conditions
                orderType=order_type,
                qty=qty,
                price="61600",
                timeInForce=time_in_force,
                
                isLeverage=is_leverage,
                
            )
        resp = {"message": "Order placed successfully!", 'response_data': response}  # Replace {...} with actual response data
        return JsonResponse(resp)    
        
def place_sell_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Get form data
            category = form.cleaned_data['category']
            symbol = form.cleaned_data['symbol']
            order_type = form.cleaned_data['orderType']
            # qty = form.cleaned_data['qty']
            price = form.cleaned_data['price']
            time_in_force = form.cleaned_data['timeInForce']
            order_link_id = form.cleaned_data['orderLinkId']
            is_leverage = form.cleaned_data['isLeverage']
            order_filter = form.cleaned_data['orderFilter']
            
            # Place a sell order
            session = HTTP(testnet=True, api_key="api", api_secret="XXXXX")
            response = session.place_order(
                category=category,
                symbol=symbol,
                side="Sell",  # Specify the side as Sell
                orderType=order_type,
                # qty=qty,
                price=price,
                timeInForce=time_in_force,
                orderLinkId=order_link_id,
                isLeverage=is_leverage,
                orderFilter=order_filter
            )
            resp = {"message": "SELL placed successfully!", 'response_data': response}  # Replace {...} with actual response data
            return JsonResponse(resp) 
        else:
            # Form is not valid, return error response
            return JsonResponse({"error": "Form data is not valid."}, status=400)
    else:
        # Request method is not POST, return error response
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

def order_form(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Get form data
            exchange="BINANCE"
            # exchange = form.cleaned_data['exchange']
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            indicators_type = form.cleaned_data['indicators_type']
            indicator1 = form.cleaned_data['indicators1']
            indicator2 = form.cleaned_data['indicators2']
            category = form.cleaned_data['category']
            symbol = form.cleaned_data['symbol']
            order_type = form.cleaned_data['orderType']
            # qty = form.cleaned_data['qty']
            price = form.cleaned_data['price']
            time_in_force = form.cleaned_data['timeInForce']
            order_link_id = form.cleaned_data['orderLinkId']
            is_leverage = form.cleaned_data['isLeverage']
            order_filter = form.cleaned_data['orderFilter']
            # Construct API payload
            payload = {
                "secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjYzZTUzMzBmNWFmOTRlZWNlNzFiODgzIiwiaWF0IjoxNzE1MzYwNjA0LCJleHAiOjMzMjE5ODI0NjA0fQ.B132F5h9XA-94vhHtS_Ky7Z9kfxVnDOI5QUOod1Od_0",
                "construct": {
                    "exchange": exchange,
                    "symbol": 'BTC/USDT',
                    "interval": interval,
                    "indicators": [
                      {
                        "indicator": indicators_type,
                        "period": indicator1
                      },
                      {
                        "indicator": indicators_type,
                        "period": indicator2
                      }
    ]                }
            }

            # Make API request
            response = requests.post("https://api.taapi.io/bulk", json=payload)
            response_data = response.json()
            response_data['form_data'] = {
                'category': category,
                'symbol': symbol,
                'order_type': order_type,
                # 'qty': qty,
                'price': price,
                'time_in_force': time_in_force,
                'order_link_id': order_link_id,
                'is_leverage': is_leverage,
                'order_filter': order_filter
            }
            # print(response_data)
            return render(request, 'order_placed.html', {'response_data': response_data})

    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form})

def order_placed(request):
    # This view function will simply render the order placed page
    return render(request, 'order_form.html')

def fetch_wallet_balance(request):
    # Assuming you have stored API key and secret securely on the server-side
    
    session = HTTP(
    
    api_key = api,
    api_secret = secret
)
    
    response = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="BTC",
    )

    # Return the wallet balance in JSON response
    return JsonResponse(response)

def get_kline_data(symbol, interval, limit=500):
    url = f"https://api.binance.com/api/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None
    







# def api_form_view(request):
#     if request.method == 'POST':
#         form = ApiForm(request.POST)
#         if form.is_valid():
#             # Process the form data
#             apikey = form.cleaned_data['apikey']
#             secretkey = form.cleaned_data['secretkey']
#             symbol = form.cleaned_data['symbol']
#             lowMA = form.cleaned_data['lowMA']
#             highMA = form.cleaned_data['highMA']
#             print(apikey,secretkey,symbol,lowMA,highMA)
#             payload = {
#                 "secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjYzZTUzMzBmNWFmOTRlZWNlNzFiODgzIiwiaWF0IjoxNzE1MzYwNjA0LCJleHAiOjMzMjE5ODI0NjA0fQ.B132F5h9XA-94vhHtS_Ky7Z9kfxVnDOI5QUOod1Od_0",
#                 "construct": {
#             # Use your desired parameters here BTC/USDT
#                 "exchange": "binance",
#                 "symbol": 'BTC/USDT',
#                 "interval": "5m",
#                 "indicators": [{"indicator": "ma", "period": lowMA}, {"indicator": "ma", "period": highMA}]
#         }
#     }
#             response = requests.post("https://api.taapi.io/bulk", json=payload)
#             data = response.json()
#             lowma = data['data'][0]['result']['value']
#             highma = data['data'][1]['result']['value']
#             print(lowma,highma)
#             response= check_ma_crossover(lowma,highma,request,form,apikey,secretkey,symbol)
                
#         else:
#                 # Handle case where MA values are unavailable
#                 message = "Unable to retrieve Moving Averages. Please check your API or data source."
#                 return render(request, 'success.html', context={
#                     'form': form,
#                     'message': message,
#                 })

#     # GET request or invalid form submission
#     form = ApiForm()
#     return render(request, 'api_form.html', {'form': form})

# def check_ma_crossover(lowma,highma,request,form,apikey,secretkey,symbol):
    
#     if lowma is not None and highma is not None:
#         print("function ki 1st condition")
#         if lowma > highma:
#             crossover_message = "MA Crossover Detected: Bullish Signal!"
#             print("function chal rha")
#             def get_time_stamp():
#                 d = datetime.datetime.utcnow()
#                 epoch = datetime.datetime(1970, 1, 1)
#                 return str(int((d - epoch).total_seconds()))

#             timestamp = get_time_stamp()
#             endpoint_path = '/v2/wallet/balances'
#             message = f'GET{timestamp}{endpoint_path}'
#             signature = hmac.new(secretkey.encode(), message.encode(), hashlib.sha256).hexdigest()
#             headers = {
#                 'Accept': 'application/json',
#                 'api-key': apikey,
#                 'signature': signature,
#                 'timestamp': timestamp
#                 }
#             response = requests.get(f'https://api.delta.exchange{endpoint_path}', headers=headers)
#             data = response.json()
#             # print(data)
#             wallet_balance = None
#             for asset in data['result']:
#                 if asset['asset_id'] == 5:
#                     wallet_balance = asset['balance']
#                     break
#             try:
#                 wallet_balance=float(wallet_balance) 
#                 print(wallet_balance)   
#                 if wallet_balance > 0:
#                     def generate_signature(secret, message):
#                         message = bytes(message, 'utf-8')
#                         secret = bytes(secret, 'utf-8')
#                         hash = hmac.new(secret, message, hashlib.sha256)
#                         return hash.hexdigest()
#                     def get_time_stamp():
#                         d = datetime.datetime.utcnow()
#                         epoch = datetime.datetime(1970,1,1)
#                         return str(int((d - epoch).total_seconds()))
#                     url = "https://api.delta.exchange/v2/orders"
#                     delta_client = DeltaRestClient(
#                     base_url='https://api.delta.exchange',
#                     api_key=apikey,
#                     api_secret=secretkey
#                     )
#                     symbol_response = delta_client.get_ticker(symbol)
#                     method = 'POST'
#                     timestamp = get_time_stamp()
#                     path = '/v2/orders'
#                     query_string = ''
#                     size=str(wallet_balance/float(str(symbol_response['spot_price'])))
#                     payload = "{\"order_type\":\"limit_order\",\"size\":"+size+",\"side\":\"buy\",\"limit_price\":\"" + str(symbol_response['spot_price']) + "\",\"product_id\":84}"
#                     signature_data = method + timestamp + path + query_string + payload
#                     signature = generate_signature(secretkey, signature_data)
#                     req_headers = {
#                         'api-key': apikey,
#                         'timestamp': timestamp,
#                         'signature': signature,
#                         'User-Agent': 'rest-client',
#                         'Content-Type': 'application/json'
#                         }
#                     response = requests.request(method, url, data=payload, params={}, timeout=(3, 27), headers=req_headers)
#                 # print(response)
#                 # return render(request, 'success.html', context={
#                 #     'form': form,
#                 #     'crossover_message': crossover_message,
#                 # })
#                     print(response)
#             except ValueError:
#                     return render(request, 'success.html', context={
#                         'form': form,
#                         'crossover_message': crossover_message,
#                         })               
#     else:
#         if lowma < highma:
#             crossover_message = "No MA Crossover: Bearish Signal."
#             print("MA 50 crossed below MA 200 - Bearish signal!")


def api_form_view(request):
    if request.method == 'POST':
        form = ApiForm(request.POST)
        if form.is_valid():
            # Process the form data
            apikey = form.cleaned_data['apikey']
            secretkey = form.cleaned_data['secretkey']
            symbol = form.cleaned_data['symbol']
            lowMA = form.cleaned_data['lowMA']
            highMA = form.cleaned_data['highMA']
            interval = form.cleaned_data['interval']
            print(apikey, secretkey, symbol, lowMA, highMA)
            payload = {
                "secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjYzZTUzMzBmNWFmOTRlZWNlNzFiODgzIiwiaWF0IjoxNzE1MzYwNjA0LCJleHAiOjMzMjE5ODI0NjA0fQ.B132F5h9XA-94vhHtS_Ky7Z9kfxVnDOI5QUOod1Od_0",
                "construct": {
                    # Use your desired parameters here BTC/USDT
                    "exchange": "binance",
                    "symbol": 'BTC/USDT',
                    "interval":interval,
                    "indicators": [{"indicator": "ma", "period": lowMA}, {"indicator": "ma", "period": highMA}]
                }
            }
            response = requests.post("https://api.taapi.io/bulk", json=payload)
            data = response.json()
            lowma = data['data'][0]['result']['value']
            highma = data['data'][1]['result']['value']
            print(lowma, highma)
            if lowma is not None and highma is not None:
                if lowma > highma:
                    response = check_ma_crossover(lowma, highma, request, form, apikey, secretkey, symbol)
                elif lowma < highma:
                    response = check_ma_crossover_for_sell(lowma, highma, request, form, apikey, secretkey, symbol)


        else:
            # Handle case where MA values are unavailable
            message = "Unable to retrieve Moving Averages. Please check your API or data source."
            return render(request, 'success.html', context={
                'form': form,
                'message': message,
            })

    # GET request or invalid form submission
    form = ApiForm()
    return render(request, 'api_form.html', {'form': form})

def check_ma_crossover(lowma, highma, request, form, apikey, secretkey, symbol):
    if lowma is not None and highma is not None:
        print("Function: MA crossover condition met")
        if lowma > highma:
            crossover_message = "MA Crossover Detected: Bullish Signal!"
            print("Function: Bullish crossover detected")
            
            def get_time_stamp():
                d = datetime.datetime.utcnow()
                epoch = datetime.datetime(1970, 1, 1)
                return str(int((d - epoch).total_seconds()))

            timestamp = get_time_stamp()
            endpoint_path = '/v2/wallet/balances'
            message = f'GET{timestamp}{endpoint_path}'
            signature = hmac.new(secretkey.encode(), message.encode(), hashlib.sha256).hexdigest()
            headers = {
                'Accept': 'application/json',
                'api-key': apikey,
                'signature': signature,
                'timestamp': timestamp
            }
            response = requests.get(f'https://api.delta.exchange{endpoint_path}', headers=headers)
            data = response.json()
            print("Wallet balance response:", data)
            
            wallet_balance = None
            for asset in data['result']:
                if asset['asset_id'] == 5:
                    wallet_balance = asset['balance']
                    break
            
            try:
                wallet_balance = float(wallet_balance)
                print("Wallet Balance:", wallet_balance)   
                if wallet_balance > 0:
                    def generate_signature(secret, message):
                        message = bytes(message, 'utf-8')
                        secret = bytes(secret, 'utf-8')
                        hash = hmac.new(secret, message, hashlib.sha256)
                        return hash.hexdigest()

                    def get_time_stamp():
                        d = datetime.datetime.utcnow()
                        epoch = datetime.datetime(1970,1,1)
                        return str(int((d - epoch).total_seconds()))

                    url = "https://api.delta.exchange/v2/orders"
                    delta_client = DeltaRestClient(
                        base_url='https://api.delta.exchange',
                        api_key=apikey,
                        api_secret=secretkey
                    )
                    symbol_response = delta_client.get_ticker(symbol)
                    print("Symbol response:", symbol_response)

                    method = 'POST'
                    timestamp = get_time_stamp()
                    path = '/v2/orders'
                    query_string = ''
                    size = str(wallet_balance / float(symbol_response['spot_price']))
                    payload = {
                        "order_type": "limit_order",
                        "size": 1,
                        "side": "buy",
                        "limit_price": str(symbol_response['spot_price']),
                        "product_id": 139
                    }
                    payload_json = json.dumps(payload)
                    print("Payload:", payload_json)

                    signature_data = method + timestamp + path + query_string + payload_json
                    signature = generate_signature(secretkey, signature_data)
                    
                    req_headers = {
                        'api-key': apikey,
                        'timestamp': timestamp,
                        'signature': signature,
                        'User-Agent': 'rest-client',
                        'Content-Type': 'application/json'
                    }

                    response = requests.request(method, url, data=payload_json, params={}, timeout=(3, 27), headers=req_headers)
                    print("Order response:", response.json())
                    return render(request, 'success.html', context={
                        'form': form,
                        'crossover_message': crossover_message,
                    })
            except ValueError as e:
                print("ValueError:", e)
                return render(request, 'success.html', context={
                    'form': form,
                    'crossover_message': crossover_message,
                })               
    else:
        if lowma < highma:
            crossover_message = "No MA Crossover: Bearish Signal."
            print("Function: Bearish crossover detected")

def check_ma_crossover_for_sell(lowma, highma, request, form, apikey, secretkey, symbol):
    if lowma is not None and highma is not None:
        print("Function: MA crossover condition met")
        if lowma > highma:
            crossover_message = "MA Crossover Detected: Bullish Signal!"
            print("Function: Bullish crossover detected")
            
            def get_time_stamp():
                d = datetime.datetime.utcnow()
                epoch = datetime.datetime(1970, 1, 1)
                return str(int((d - epoch).total_seconds()))

            timestamp = get_time_stamp()
            endpoint_path = '/v2/wallet/balances'
            message = f'GET{timestamp}{endpoint_path}'
            signature = hmac.new(secretkey.encode(), message.encode(), hashlib.sha256).hexdigest()
            headers = {
                'Accept': 'application/json',
                'api-key': apikey,
                'signature': signature,
                'timestamp': timestamp
            }
            response = requests.get(f'https://api.delta.exchange{endpoint_path}', headers=headers)
            data = response.json()
            print("Wallet balance response:", data)
            
            wallet_balance = None
            for asset in data['result']:
                if asset['asset_id'] == 5:
                    wallet_balance = asset['balance']
                    break
            
            try:
                wallet_balance = float(wallet_balance)
                print("Wallet Balance:", wallet_balance)   
                if wallet_balance > 0:
                    def generate_signature(secret, message):
                        message = bytes(message, 'utf-8')
                        secret = bytes(secret, 'utf-8')
                        hash = hmac.new(secret, message, hashlib.sha256)
                        return hash.hexdigest()

                    def get_time_stamp():
                        d = datetime.datetime.utcnow()
                        epoch = datetime.datetime(1970,1,1)
                        return str(int((d - epoch).total_seconds()))

                    url = "https://api.delta.exchange/v2/orders"
                    delta_client = DeltaRestClient(
                        base_url='https://api.delta.exchange',
                        api_key=apikey,
                        api_secret=secretkey
                    )
                    symbol_response = delta_client.get_ticker(symbol)
                    print("Symbol response:", symbol_response)

                    method = 'POST'
                    timestamp = get_time_stamp()
                    path = '/v2/orders'
                    query_string = ''
                    size = str(wallet_balance / float(symbol_response['spot_price']))
                    payload = {
                        "order_type": "limit_order",
                        "size": 1,
                        "side": "sell",
                        "limit_price": str(symbol_response['spot_price']),
                        "product_id": 139
                    }
                    payload_json = json.dumps(payload)
                    print("Payload:", payload_json)

                    signature_data = method + timestamp + path + query_string + payload_json
                    signature = generate_signature(secretkey, signature_data)
                    
                    req_headers = {
                        'api-key': apikey,
                        'timestamp': timestamp,
                        'signature': signature,
                        'User-Agent': 'rest-client',
                        'Content-Type': 'application/json'
                    }

                    response = requests.request(method, url, data=payload_json, params={}, timeout=(3, 27), headers=req_headers)
                    print("Order response:", response.json())
                    return render(request, 'success.html', context={
                        'form': form,
                        'crossover_message': crossover_message,
                    })
            except ValueError as e:
                print("ValueError:", e)
                return render(request, 'success.html', context={
                    'form': form,
                    'crossover_message': crossover_message,
                })               
    else:
        if lowma < highma:
            crossover_message = "No MA Crossover: Bearish Signal."
            print("Function: Bearish crossover detected")
