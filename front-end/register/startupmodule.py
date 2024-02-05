import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import open_form
import login_flow

# Open the home page on app startup.
login_flow.do_email_confirm_or_reset()
open_form('Home')