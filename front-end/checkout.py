from ._anvil_designer import CheckoutTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Register import login_flow

class Checkout(CheckoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Set form details.
    self.update_login_status()
    self.refresh_cart()
    self.repeating_panel_cart.set_event_handler('x-refresh-cart', self.refresh_cart)

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

  def refresh_cart(self, **event_args):
    # Refresh the cart page.
    check_cart_rows = anvil.server.call('check_cart_rows')
    if check_cart_rows == []:
      self.checkout_button.text = "0 | Cart"
      self.empty_cart_image.visible = True
    else: 
      cart_number = str(len(check_cart_rows))
      self.checkout_button.text = cart_number + " | Cart"
      self.empty_cart_image.visible = False
      
    # Refresh the cart button.
    self.repeating_panel_cart.items = anvil.server.call('get_cart')
    user = anvil.users.get_user()
    total_price = 0
    price_list = [row['price']*int(row['item_quantity']) for row in app_tables.cart.search()]
    for prices in range(0, len(price_list)):
      total_price = total_price + price_list[prices]
    self.total_price.text = '$' + "{:.2f}".format(total_price)
    
  def payment_button_click(self, **event_args):
    # Confirm payment with the user and clear form contents.
    check_cart_rows = anvil.server.call('check_cart_rows')
    if check_cart_rows == []:
      alert("Please add some items to your cart before payment.")
    if self.address_line_1_box.text == '' or self.city_box.text == '' or self.postcode_box.text == ''\
    or self.card_name_box.text == '' or self.card_number_box.text == ''\
    or self.date_picker_expiration.date == None or self.cvc_box.text == '':
      alert("Please enter delivery and payment details.")
    else: 
      alert("Payment confirmed! Your order will be delivered to you.")
      app_tables.cart.delete_all_rows()
      self.special_instructions_box.text = ''
      self.address_line_1_box.text = ''
      self.address_line_2_box.text = ''
      self.city_box.text = ''
      self.postcode_box.text = ''
      self.card_name_box.text = ''
      self.card_number_box.text = ''
      self.date_picker_expiration.date = None
      self.cvc_box.text = ''
      self.refresh_cart()