from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
# from keys import secret,api
User = get_user_model()  # Replace with your custom User model if applicable

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')  # Add other fields as needed

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Hash password before saving
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Invalid username or password.')
        return user


class KlineForm(forms.Form):
    category = forms.ChoiceField(choices=[('inverse', 'Inverse'), ('linear', 'Linear')], label='Category')
    symbol = forms.CharField(label='Symbol (e.g., BTCUSD)')
    interval = forms.IntegerField(label='Interval (in minutes)', min_value=1)
    # num_intervals = forms.IntegerField(label='Number of Intervals (e.g., 5 for 5 minutes of data)', min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        interval = cleaned_data.get('interval')

        # Validate interval as a multiple of 60 (optional)
        # if interval % 60 != 0:
        #     raise forms.ValidationError('Interval must be a multiple of 60 minutes.')

        # Ensure num_intervals is valid
        # num_intervals = cleaned_data.get('num_intervals')
        # if num_intervals <= 0:
        #     raise forms.ValidationError('Number of intervals must be greater than 0.')

        return cleaned_data



class BybitDataForm(forms.Form):
  symbol = forms.CharField(max_length=10, label="Symbol (e.g., BTCUSD)")
  category = forms.ChoiceField(choices=[("linear", "Linear"), ("inverse", "Inverse")], label="Category")
  interval = forms.IntegerField(min_value=1, label="Interval (minutes)")
  limit = forms.IntegerField(min_value=1, label="Data Points Limit", initial=50)

class TAAPIForm(forms.Form):
  """
  Form class for user input of TAAPI request parameters.
  """
  exchange = forms.CharField(label="Exchange", max_length=100)
  symbol = forms.CharField(label="Symbol", max_length=100)
  interval = forms.CharField(label="Interval", max_length=10)
  indicators = forms.MultipleChoiceField(label="Indicators", choices=[
      ("ma_50", "Moving Average (50)"),
      ("ma_200", "Moving Average (200)"),
      # Add more indicator choices as needed
  ])

  def clean_indicators(self):
      """
      Custom validation for indicators field (optional).
      """
      # You can add validation logic here, e.g., ensure at least one indicator is selected.
      return self.cleaned_data['indicators']

# order set form
class OrderForm(forms.Form):
    # Part 1: Indicators
    exchange = forms.ChoiceField(label="Exchange",  choices=[("bybit", "bybit")])
    symbol = forms.CharField(label="Symbol", max_length=100)
    interval = forms.CharField(label="Interval", max_length=10)
    # indicators = forms.MultipleChoiceField(label="Indicators", choices=[
    #     ("ma_50", "Moving Average (50)"),
    #     ("ma_200", "Moving Average (200)"),
    indicators_type = forms.ChoiceField(label="Indicators Type",  choices=[("ma", "ma")])
    indicators1 = forms.IntegerField(label="Indicators1", min_value=0)
    indicators2 = forms.IntegerField(label="Indicators2", min_value=0)
        # Add more indicator choices as needed
    

    def clean_indicators(self):
        """
        Custom validation for indicators field (optional).
        """
        # You can add validation logic here, e.g., ensure at least one indicator is selected.
        return self.cleaned_data['indicators']

    # Part 2: Order Parametersspot, linear, inverse, option
    category = forms.ChoiceField(label="Category", choices=[("spot", "Spot"), ("option", "option"),("inverse", "inverse"), ("linear", "linear")])
    side = forms.ChoiceField(label="Side", choices=[("Buy", "Buy"), ("Sell", "Sell")])
    orderType = forms.ChoiceField(label="Order Type", choices=[("Market", "Market"), ("Limit", "Limit")])
    # qty = forms.FloatField(label="Quantity")
    price = forms.FloatField(label="Invest Amount")

    timeInForce = forms.ChoiceField(label="Time in Force", choices=[("GTC", "GTC"), ("IOC", "IOC"), ("FOK", "FOK"), ("PostOnly", "PostOnly")])
    orderLinkId = forms.CharField(label="Order Link ID", max_length=100)
    isLeverage = forms.IntegerField(label="Is Leverage", min_value=0, max_value=1)
    orderFilter = forms.ChoiceField(label="Order Filter", choices=[("Order", "Order"), ("Market", "Market")])
  


class ApiForm(forms.Form):
    apikey = forms.CharField(max_length=100, label='API Key')
    secretkey = forms.CharField(max_length=100, label='Secret Key', widget=forms.PasswordInput)
    symbol = forms.CharField(max_length=20, label='Symbol')
    lowMA = forms.IntegerField(label='Low Moving Average')
    highMA = forms.IntegerField(label='High Moving Average')
    interval=forms.CharField(label='Interval (e.g., 1m,15m,1h,1D)')