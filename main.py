import anvil.email
import tables
from tables import app_tables
import anvil.users
import anvil.server
from anvil.http import url_encode
import bcrypt
from random import SystemRandom
random = SystemRandom()
import sys
from datetime import datetime

"""
         ____      _               _____      _               
        |  _ \ ___| |_ _ __ ___   | ____|__ _| |_ ___         
 _____  | |_) / _ \ __| '__/ _ \  |  _| / _` | __/ __|  _____ 
|_____| |  _ <  __/ |_| | | (_) | | |__| (_| | |_\__ \ |_____|
        |_| \_\___|\__|_|  \___/  |_____\__,_|\__|___/        


                                         .""--..__
                     _                     []       ``-.._
                  .'` `'.                  ||__           `-._
                 /    ,-.\                 ||_ ```---..__     `-.
                /    /:::\\               /|//}          ``--._  `.
                |    |:::||              |////}                `-. \
                |    |:::||             //'///                    `.\
                |    |:::||            //  ||'                      `|
                /    |:::|/        _,-//\  ||
               /`    |:::|`-,__,-'`  |/  \ ||
             /`  |   |'' ||           \   |||
           /`    \   |   ||            |  /||
         |`       |  |   |)            \ | ||
        |          \ |   /      ,.__    \| ||
        /           `         /`    `\   | ||
       |                     /        \  / ||
       |                     |        | /  ||
       /         /           |        `(   ||
      /          .           /          )  ||
     |            \          |     ________||
    /             |          /     `-------.|
   |\            /          |              ||
   \/`-._       |           /              ||
    //   `.    /`           |              ||
   //`.    `. |             \              ||
  ///\ `-._  )/             |              ||
 //// )   .(/               |              ||
 ||||   ,'` )               /              //
 ||||  /                    /             || 
 `\\` /`                    |             // 
     |`                     \            ||  
    /                        |           //  
  /`                          \         //   
/`                            |        ||    
`-.___,-.      .-.        ___,'        (/    
         `---'`   `'----'`
"""

def mk_token():
  # Generate a random 14-character token.
  return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for i in range(14)])

@anvil.server.callable
def _send_password_reset(email):
  """Send a password reset email to the specified user"""
  user = app_tables.users.get(email=email)
  if user is not None:
    user['link_key'] = mk_token()
    anvil.email.send(to=user['email'], subject="Reset your password", text=f"""
Hi,

Someone has requested a password reset for your account. If this wasn't you, just delete this email.
If you do want to reset your password, click here:

{anvil.server.get_app_origin('published')}#?email={url_encode(user['email'])}&pwreset={url_encode(user['link_key'])}

Thanks!
""")
    return True


@anvil.server.callable
def _send_email_confirm_link(email):
  # Send an email confirmation link if the specified user's email is not yet confirmed.
  user = app_tables.users.get(email=email)
  if user is not None and not user['confirmed_email']:
    if user['link_key'] is None:
      user['link_key'] = mk_token()
    anvil.email.send(to=user['email'], subject="Confirm your email address", text=f"""
Hi,

Thanks for signing up for Retro Eats. To complete your sign-up, click here to confirm your email address:

{anvil.server.get_app_origin('published')}#?email={url_encode(user['email'])}&confirm={url_encode(user['link_key'])}

Thanks!
""")
    return True

def hash_password(password, salt):
  # Hash the password so passwords are protected in case of data leaks.
  if not isinstance(password, bytes):
    password = password.encode()
  if not isinstance(salt, bytes):
    salt = salt.encode()

  result = bcrypt.hashpw(password, salt)

  if isinstance(result, bytes):
    return result.decode('utf-8')


@anvil.server.callable
def _do_signup(email, phone_number, name, password, sex, age, dietary_comments):
  # Add the user in a transaction, to make sure there is only ever one user in this database with this email address.
  if name is None or name.strip() == "":
    return "Must supply a name"
  
  pwhash = hash_password(password, bcrypt.gensalt())
  
  @tables.in_transaction
  def add_user_if_missing():
    # Add the user if missing from the users table.
    user = app_tables.users.get(email=email)
    if user is None:
      user = app_tables.users.add_row(email=email, enabled=True, phone_number=phone_number, name=name, 
      password_hash=pwhash, sex=sex, age=age, dietary_comments=dietary_comments)
      return user
    
  user = add_user_if_missing()

  if user is None:
    return "This email address has already been registered for our service. Try logging in."
  
  _send_email_confirm_link(email)
  
  # No error = success
  return None
  
    
def get_user_if_key_correct(email, link_key):
  # Hash the link key and compare the hashed version.
  user = app_tables.users.get(email=email)

  if user is not None and user['link_key'] is not None:
    salt = bcrypt.gensalt()
    if hash_password(link_key, salt) == hash_password(user['link_key'], salt):
      return user


@anvil.server.callable
def _is_password_key_correct(email, link_key):
  # Check if password key is correct.
  return get_user_if_key_correct(email, link_key) is not None

@anvil.server.callable
def _perform_password_reset(email, reset_key, new_password):
  # Perform a password reset if the key matches; return True if it did.
  user = get_user_if_key_correct(email, reset_key)
  if user is not None:
    user['password_hash'] = hash_password(new_password, bcrypt.gensalt())
    user['link_key'] = None
    anvil.users.force_login(user)
    return True
    
@anvil.server.callable
def _confirm_email_address(email, confirm_key):
  # Confirm a user's email address if the key matches; return True if it did.
  user = get_user_if_key_correct(email, confirm_key)
  if user is not None:
    user['confirmed_email'] = True
    user['link_key'] = None
    anvil.users.force_login(user)
    return True

@anvil.server.callable
def _update_user(user, name, phone_number, sex, age, dietary_comments):
  # Update user information in the user data table.
  user.update(name=name, phone_number=phone_number, 
              sex=sex, age=age, dietary_comments=dietary_comments)

@anvil.server.callable
def get_menu():
  # Fill menu table with menu data table.
  return app_tables.menu.search(tables.order_by("featured", ascending=False))
  
@anvil.server.callable
def search_menu(query):
  # Search menu table for keyword.
  result = app_tables.menu.search()
  if query:
    result = [
      search for search in result
      if query in search['item_name']
      or query in search['description']
    ]
  return result

@anvil.server.callable
def get_cart():
  # Fill cart table with cart data table.
  return app_tables.cart.search(tables.order_by("added", ascending=False))
  
@anvil.server.callable
def check_cart_rows():
  # Check contents of the cart.
  total_items_in_cart = 0
  cart_list = [int(row['item_quantity']) for row in app_tables.cart.search()]
  for quantity in range(0, len(cart_list)):
    total_items_in_cart = total_items_in_cart + cart_list[quantity]
  return cart_list

@anvil.server.callable
def add_item_to_cart(email, name, item_name, item_quantity, price):
  # Add food item to the cart.
  query = app_tables.cart.get(item_name=item_name)
  if query is None:
    app_tables.cart.add_row(email=email, name=name, item_name=item_name, item_quantity=item_quantity, price=price, added=datetime.now())
  else:
    edited_item_row = app_tables.cart.get(item_name=item_name)
    added_quantity = edited_item_row['item_quantity']
    edited_item_row.update(item_quantity=str(int(item_quantity)+int(added_quantity)))

@anvil.server.callable
def edit_cart(cart, item_quantity):
  # Edit cart in the cart data table.
  cart.update(item_quantity=item_quantity)

@anvil.server.callable
def delete_cart(cart):
  # Delete food_item in the cart data table.
  cart.delete()