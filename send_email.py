import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from global_variables import SERVER_ADDRESS_HOST, SERVER_ADDRESS_PORT


def send_forgot_password_email(address, password):
    from_address = os.getenv('FROM')
    email_password = os.getenv('PASSWORD')

    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = address
    message['Subject'] = "Password recovery"

    # Email html text
    html = f'''<html lang="en">
<head></head>
<body>
    <h1>Voice assistant</h1>
    <p>You've clicked "Forgot password?" button on our login page.<br>
    Here is your new password:</p>
    <h3>{password}</h3>
    If you didn't want to change your password, click <a href="http://{SERVER_ADDRESS_HOST}:{SERVER_ADDRESS_PORT}/revert-password">here</a> to revert it.
</body>
</html>'''
    message.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP_SSL(os.getenv('HOST'), os.getenv('PORT'))  # Create a server
    server.login(from_address, email_password)  # Log in to the server

    server.sendmail(msg=message.as_string(),
                    from_addr=from_address,
                    to_addrs=address)  # Send the email
    server.quit()  # Quit the server
    return True
