from ._anvil_designer import RowTemplateCheckoutTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplateCheckout(RowTemplateCheckoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def edit_cart(self, **event_args):
    # Edit item in cart.
    anvil.server.call('edit_cart', self.item, item_quantity=self.drop_down_item_quantity.selected_value)
    self.parent.raise_event('x-refresh-cart')

  def delete_button_click(self, **event_args):
    # Delete item in cart.
    anvil.server.call('delete_cart', self.item)
    self.parent.raise_event('x-refresh-cart')