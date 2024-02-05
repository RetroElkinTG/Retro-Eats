from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from LoginDialog import LoginDialog
from SignupDialog import SignupDialog
from ForgottenPasswordDialog import ForgottenPasswordDialog
from PasswordResetDialog import PasswordResetDialog

def login_with_form(allow_cancel=True):
  # Log in by popping up the LoginDialog form.
  d = LoginDialog()

  BUTTONS = [("Log in", "login", "primary")]
  if allow_cancel:
    BUTTONS += [("Cancel", None)]
  
  while anvil.users.get_user() is None:
    choice = alert(d, title="Log In", dismissible=allow_cancel, buttons=BUTTONS)
    
    if choice == 'login':
      try:
        anvil.users.login_with_email(d.email_box.text, d.password_box.text, remember=True)
      except anvil.users.EmailNotConfirmed:
        d.confirm_lnk.visible = True
      except anvil.users.AuthenticationFailed as e:
        d.login_err_lbl.text = str(e.args[0])
        d.login_err_lbl.visible = True
        
    elif choice == 'reset_password':
      fp = ForgottenPasswordDialog(d.email_box.text)
      
      if alert(fp, title='Forgot Password', buttons=[("Reset password", True, "primary"), ("Cancel", False)]):
        
        if anvil.server.call('_send_password_reset', fp.email_box.text):
          alert(f"A password reset email has been sent to {fp.email_box.text}.")
        else:
          alert("That username does not exist in our records.")
        
    elif choice == 'confirm_email':
      if anvil.server.call('_send_email_confirm_link', d.email_box.text):
        alert(f"A new confirmation email has been sent to {d.email_box.text}.")
      else:
        alert(f"'{d.email_box.text}' is not an unconfirmed user account.")
      d.confirm_lnk.visible = False
    
    elif choice is None and allow_cancel:
      break

      
def signup_with_form():
  # Sign up the user with the SignupDialog form.
  d = SignupDialog()

  while True:
    if not alert(d, title="Sign Up", buttons=[("Sign Up", True, 'primary'), ("Cancel", False)]):
      return
    
    if d.password_box.text != d.password_repeat_box.text:
      d.signup_err_lbl.text = 'Passwords do not match. Try again.'
      d.signup_err_lbl.visible = True
      continue
    
    err = anvil.server.call('_do_signup', d.email_box.text, d.phone_number_box.text, d.name_box.text, d.password_box.text, 
    d.sex_box.selected_value, d.age_box.text, d.dietary_comments_box.text)
    if err is not None:
      d.signup_err_lbl.text = err
      d.signup_err_lbl.visible = True
    else:
      alert(f"We have sent a confirmation email to {d.email_box.text}.\n\nCheck your email, and click on the link.")
      return
  
    
def do_email_confirm_or_reset():
  # Check whether the user has arrived from an email-confirmation link or a password reset, and pop up any necessary dialogs.
  h = anvil.get_url_hash()
  if isinstance(h, dict) and 'email' in h:
    if 'pwreset' in h:
      if not anvil.server.call('_is_password_key_correct', h['email'], h['pwreset']):
        alert("This is not a valid password reset link")
        return

      while True:
        pwr = PasswordResetDialog()
        if not alert(pwr, title="Reset Your Password", buttons=[("Reset password", True, 'primary'), ("Cancel", False)]):
          return
        if pwr.pw_box.text != pwr.pw_repeat_box.text:
          alert("Passwords did not match. Try again.")
        else:
          break
  
      if anvil.server.call('_perform_password_reset', h['email'], h['pwreset'], pwr.pw_box.text):
        alert("Your password has been reset. You are now logged in.")
      else:
        alert("This is not a valid password reset link")

        
    elif 'confirm' in h:
      if anvil.server.call('_confirm_email_address', h['email'], h['confirm']):
        alert("Thanks for confirming your email address. You are now logged in.")
      else:
        alert("This confirmation link is not valid. Perhaps you have already confirmed your address?\n\nTry logging in normally.")