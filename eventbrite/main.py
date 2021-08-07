from eventbrite_util import eventbrite_autobuyer
import time
import smtplib, ssl

# Input login credentials
email = ''
key = ''
cardNumber='1234123412341234'
expDate='02/22'
cvv = '123'
postal = '11111'
firstName = ''
lastName = ''

#para esto se ocupa un sender email que tenga less secure apps enabled
notifications = False
sender = ''
receiver = ''
pwd = ''

eventUrlPurdue = "https://www.eventbrite.com/e/here-come-the-irish-tickets-165803612067?aff=eprofsaved"
eventUrlTest = "https://www.eventbrite.com/e/kes-the-band-iz-we-ny-labor-day-tickets-162167987817?aff=ebdssbcitybrowse"

signIn = False
maxSignInTries = 3
isTest = True
maxTries = 3
refreshRate = 3 #seconds
numTickets =  1
timeout = 30 #seconds

port = 465
context = ssl.create_default_context()

success = False

num_tries = 0

while not success and num_tries <= maxTries:
    tac = time.perf_counter()
    success = eventbrite_autobuyer(isTest, firstName, lastName, email, key, cardNumber, expDate, cvv, postal, signIn, maxSignInTries, eventUrlTest, refreshRate, numTickets, timeout)
    print('Performance: ', time.perf_counter() - tac, ' sec')

    if success:
        message = "Purchase succesful."
    elif not success and num_tries <= maxTries:
        message = "ERROR. Retrying..."
    else:
        message = "ERROR. " + str(maxTries) + " tries unsuccesful. Restart program."

    if not isTest and notifications:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, pwd)
            server.sendmail(sender, receiver, message)
    
    num_tries += 1