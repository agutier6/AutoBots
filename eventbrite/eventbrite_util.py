from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

'''
This program executes a bot that buys eventbrite tickets for nd vs purdue tailgate

TODO:
- Add address input capability for specific events
- add input error checking
- unselect email spam
- make read me

'''
def find_iframe_id(driver):
    iframes = driver.find_elements_by_xpath("//iframe")
    for index, iframe in enumerate(iframes):
        iframeID = iframe.get_attribute('id')
        if 'eventbrite-widget-modal' in iframeID:
            return iframeID
        driver.switch_to.frame(index)
        find_iframe_id(driver)
        driver.switch_to.parent_frame()
    return None

def get_all_ticket_inputs(driver, timeout):
    try:
        wait = WebDriverWait(driver, timeout)
        inputs = driver.find_elements_by_xpath("//input")
        ticket_inputs = {'N-first_name': [], 'N-last_name': [], 'N-email': []}
        for input in inputs:
            for key in ticket_inputs.keys():
                if key in input.get_attribute('id') and not 'buyer' in input.get_attribute('id'):
                    ticket_inputs[key].append(input)
    
        return ticket_inputs
    except Exception as e:
        print(e)
        return None


def eventbrite_autobuyer(isTest, firstName, lastName, email, key, cardNumber, expDate, 
                        cvv, postal, signIn, maxSignInTries, eventUrl, refreshRate, 
                        numTickets, timeout, selfBuy):
    if selfBuy:
        # first ticket assigned to buyer
        tickets = {'N-first_name': [firstName], 'N-last_name': [lastName], 'N-email': [email]}
    else:
        tickets = {'N-first_name': [], 'N-last_name': [], 'N-email': []}

    while len(tickets['N-first_name']) < numTickets:
        recipientFirstName = input('Recipient ' + str(len(tickets['N-first_name'])) + ' first name: ')
        recipientLastName = input('Recipient ' + str(len(tickets['N-first_name'])) + ' last name: ')
        recipientEmail = input('Recipient ' + str(len(tickets['N-first_name'])) + ' email: ')
        tickets['N-first_name'].append(recipientFirstName)
        tickets['N-last_name'].append(recipientLastName)
        tickets['N-email'].append(recipientEmail)

    try: 
        # Set driver to desired webbrowser
        # WARNING: Need to download driver for the desired browser ... and the browser, obviously
        print('Starting up browser...')
        driver = webdriver.Firefox()

        # Sign in process. Repeats if not succesful
        # toc = time.perf_counter()
        if signIn:
            signInTries = 0
            while True:
                try: 
                    driver.get('https://www.eventbrite.com/signin/')
                
                    wait = WebDriverWait(driver, timeout)
                    print('Inputting email...')
                    wait.until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(email)
                    print('Inputting key...')
                    wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(key)
                    print('Signing in...')
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'eds-btn'))).click()
                    # Wait until new window is is opened to make sure it signed in
                    # This sets the driver to the new window
                    # It's needed because the bot has clicked on the checkout button
                    window_after = driver.window_handles[0]
                    driver.switch_to.window(window_after)
                    wait.until(EC.title_contains('Eventbrite - Discover Great Events or Create Your Own & Sell Tickets'))
                    print('Signed in')
                    break
                except:
                    print('ERROR: Sign in failed retrying...')
                    signInTries+=1
                    if signInTries >= maxSignInTries:
                        print('ERROR: Exceeded ' + str(maxSignInTries) + ' sign in tries')
                        return False

        print('Getting product page...')
        driver.get(eventUrl)

        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'micro-ticket-box__btn'))).click()

        iframeID = find_iframe_id(driver)
        if iframeID == None:
            return False
        
        driver.get(eventUrl)

        #loops until available
        while True:
            try:
                wait = WebDriverWait(driver, refreshRate)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'micro-ticket-box__btn'))).click()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, iframeID)))
                wait = WebDriverWait(driver, refreshRate)
                select = Select(wait.until(EC.presence_of_element_located((By.NAME, 'ticket-quantity-selector'))))
                select.select_by_visible_text(str(numTickets))
                print('Selected ' + str(numTickets) + ' ticket(s)')
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'eds-btn--fill'))).click()
                print('Clicked on checkout')
                break
            except:
                print('Product not available, refreshing...')
                driver.refresh()
                driver.switch_to_default_content()
        
        wait = WebDriverWait(driver, timeout)

        firstNameBox = wait.until(EC.presence_of_element_located((By.ID, 'buyer.N-first_name')))
        if not firstNameBox.get_attribute("value") == firstName:
            firstNameBox.clear()
            firstNameBox.send_keys(firstName)

        lastNameBox = wait.until(EC.presence_of_element_located((By.ID, 'buyer.N-last_name')))
        if not lastNameBox.get_attribute("value") == lastName:
            lastNameBox.clear()
            lastNameBox.send_keys(lastName)

        emailBox = wait.until(EC.presence_of_element_located((By.ID, 'buyer.N-email')))
        if emailBox.get_attribute("value") == "":
            emailBox.send_keys(email)
            wait.until(EC.presence_of_element_located((By.ID, 'buyer.confirmEmailAddress'))).send_keys(email)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-spec='accordion-list-item-CREDIT']"))).click()

        wait.until(EC.presence_of_element_located((By.ID, 'credit-card-number'))).send_keys(cardNumber)
        wait.until(EC.presence_of_element_located((By.ID, 'expiration-date'))).send_keys(expDate)
        wait.until(EC.presence_of_element_located((By.ID, 'csc'))).send_keys(cvv)
        wait.until(EC.presence_of_element_located((By.ID, 'postal-code'))).send_keys(postal)

        ticket_inputs = get_all_ticket_inputs(driver, timeout)
        
        if ticket_inputs:
            for key in tickets.keys():
                while ticket_inputs[key]:
                    ticket_input = ticket_inputs[key].pop()
                    ticket = tickets[key].pop()
                    if not ticket_input.get_attribute('value') == ticket:
                        ticket_input.clear()
                        ticket_input.send_keys(ticket)

        print('Buying...')
        if not isTest:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'eds-btn--fill'))).click()
        print('Success')
        return True

                
    except Exception as e:
        print(e)
        return False 