from ._anvil_designer import RowTemplateMenuTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplateMenu(RowTemplateMenuTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
  def add_to_cart_button_click(self, **event_args):
    # Add food item to the cart.
    item_name = self.item['item_name']
    anvil.server.call('add_item_to_cart', email=anvil.users.get_user()['email'], 
    name=anvil.users.get_user()['name'], item_name=item_name,
    item_quantity=self.drop_down_item_quantity.selected_value, price=self.item['price'])
    self.parent.raise_event('x-refresh-menu')
    alert(item_name + " added to cart.")