from ._anvil_designer import MenuTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Register import login_flow

class Menu(MenuTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Set form details.
    self.update_login_status()
    self.refresh_menu()
    self.repeating_panel_menu.set_event_handler('x-refresh-menu', self.refresh_menu)
      
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

  def search(self, **event_args):
    # Search the cart.
    self.repeating_panel_menu.items = anvil.server.call(
      'search_menu', self.menu_search.text)

  def refresh_menu(self, **event_args):
    # Refresh the menu.
    self.repeating_panel_menu.items = anvil.server.call('get_menu')

    # Refresh the cart button.
    check_cart_rows = anvil.server.call('check_cart_rows')
    if check_cart_rows == []:
      self.checkout_button.text = "0 | Cart"
    else: 
      cart_number = str(len(check_cart_rows))
      self.checkout_button.text = cart_number + " | Cart"