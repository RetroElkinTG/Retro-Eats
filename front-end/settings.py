from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Register import login_flow

class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Set form details.
    self.update_login_status()

    # Set cart quantity.
    check_cart_rows = anvil.server.call('check_cart_rows')
    if check_cart_rows == []:
      self.checkout_button.text = "0 | Cart"
    else: 
      cart_number = str(len(check_cart_rows))
      self.checkout_button.text = cart_number + " | Cart"

    # Set user settings.
    user = anvil.users.get_user()
    self.name_box.text = user['name']
    self.phone_number_box.text = user['phone_number']
    self.sex_drop_down.selected_value = user['sex']
    self.age_box.text = user['age']
    self.dietary_comments_box.text = user['dietary_comments']

  def update_login_status (self):
    # Update the login status of user.
    user = anvil.users.get_user()
    if user is None:
      self.login_status_lbl.text = "You are not logged in."
    else:
      self.login_status_lbl.text = "You are logged in as %s" % user['email']

  def login_btn_click(self, **event_args):
    # Login the user.
    login_flow.login_with_form()
    self.update_login_status()

  def logout_btn_click(self, **event_args):
    # Logout the user.
    anvil.users.logout()
    open_form('Home')

  def signup_btn_click(self, **event_args):
    # Signout the user.
    login_flow.signup_with_form()

  def checkout_button_click(self, **event_args):
    # Open the checkout page.
    user = anvil.users.get_user()
    if user is not None:
      open_form('Checkout')
    else:
      alert("Please register or login to access the checkout page.")

  def home_button_click(self, **event_args):
    # Open the home page.
    user = anvil.users.get_user()
    if user is not None:
      open_form('Home')
    else:
      alert("Please register or login to access the home page.")

  def restaurants_button_click(self, **event_args):
    # Open the restaurants page.
    user = anvil.users.get_user()
    if user is not None:
      open_form('Restaurants')
    else:
      alert("Please register or login to access the restaurants page.")

  def settings_button_click(self, **event_args):
    # Open the settings page.
    user = anvil.users.get_user()
    if user is not None:
      open_form('Settings')
    else:
      alert("Please register or login to access your settings.")

  def update_user_details_button_click(self, **event_args):
    # Update user details.
    user = anvil.users.get_user()
    name = self.name_box.text
    phone_number = int(self.phone_number_box.text)
    sex = self.sex_drop_down.selected_value
    age = self.age_box.text
    dietary_comments = self.dietary_comments_box.text
    anvil.server.call('_update_user', user, name, phone_number, sex, age, dietary_comments)