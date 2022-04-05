# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import pickle
import os.path
from bs4 import BeautifulSoup
from base64 import urlsafe_b64decode
import time
import os
from datetime import datetime
import logging
import socket
from email.mime.text import MIMEText
import base64
from collections import namedtuple


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']



def create_message(sender="californiaexperessmail@gmail.com", to="musechika@gmail.com", subject="Acess token expires soon..", message_text=''):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  message['value'] = 'robot'
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode("utf-8")).decode()}


def send_message(service, mail, user="trekmovers.alex@gmail.com"):
    try:
        message = (service.users().messages().send(userId=user, body=mail)
                   .execute())
    except Exception as ex:
        print (ex)        

        
def validate_token_time(service, token_path="secret_files/token.pickle"):
    today = datetime.today()
    created_at = datetime.strptime(time.ctime(os.path.getctime(token_path)), "%a %b %d %H:%M:%S %Y")
    timedelta = today - created_at
    if timedelta.seconds >= 6 * 24 * 60 * 60:
        user="californiaexperessmail@gmail.com"
        timerange = 7 * 24 * 60 * 60 - timedelta.seconds
        message_text = f'Attention, expiration token soon will be refreshed!\n You will be asked to proceed manually. Token will expire in less than {timerange/3600} hours.\nIn case you want to refresh it now, delete Documents/movers_optimization/secret_files/token.pickle and wait for the pop-up window.'
        message = create_message(to=user, message_text=message_text)
        send_message(service, mail=message, user=user)


def token_check(path='secret_files/token.pickle'):
    creds = None
    if os.path.exists(path):
        with open(path, 'rb') as token:
            creds = pickle.load(token)
    return creds


def refresh_token(creds, credentials_path="secret_files/credentials.json", token_path="secret_files/token.pickle"):
    refresh_counter = 0
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            os.remove(token_path)
            refresh_counter += 1
    if refresh_counter or not creds:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = 'https://www.example.com/oauth2callback'
        
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            login_hint = "californiaexperessmail@gmail.com",
            approval_prompt="force",
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')
        creds = flow.run_local_server(port=0)         
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def build_service():
    creds = token_check()
    if not creds or not creds.valid:  
        creds = refresh_token(creds)
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_unread_mails():
    service = build_service()
    validate_token_time(service)
    num_retries = 0
    response_valid = False
    scraped_profiles = []
    while num_retries < 10: 
        try: 
            unread_mail_list_request = service.users().messages().list(userId='me', q="is:unread").execute()#, q="is:unread"
            response_valid = True
            break
        except socket.timeout:
            num_retries = num_retries + 1 
            time.sleep(0.05*num_retries)
    if response_valid:
        messages = unread_mail_list_request.get('messages')
        gmail_agent = MessageGmail(service=service)
        scraped_profiles = gmail_agent.parse_messages(messages, scraped_profiles)
    return scraped_profiles


def get_encoded_message(service, msg):
    try:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        return txt
    except Exception as ex:
        logging.error(ex)
        print(ex)


class MessageGmail:
    def __init__(self, **kwargs):
        self.payload = None
        self.subject = None
        self.decoded_data = None
        self.service = kwargs.get("service")
    
    def process_decoded_data(self, msg, scraped_profiles):
        soup = self.decode_message()
        quote = None
        if soup:
            print(self.subject)
            if self.relevant_parts[0] in self.subject:
                link = soup.findAll("a")[-4].get("href") #-4
                quote = self.parse_nearby_job(soup, link)
            elif self.relevant_parts[1] in self.subject:
                link = soup.findAll("a")[-4].get("href") #-4
                quote = self.parse_direct_quote(soup, link)
        scraped_profiles.append(quote)
        return scraped_profiles

    def decode_message(self):
        parts = self.payload.get('parts')
        for part in parts:
            mtype = part.get("mimeType")
            if mtype == "text/html":
                data = part['body']['data']
                self.decoded_data = urlsafe_b64decode(data)
       #         open("decoded.txt", 'wb').write(self.decoded_data)
                soup = BeautifulSoup(self.decoded_data , "lxml")
                return soup
            
    def parse_direct_quote(self, soup, link):
        DirectQuote = namedtuple('DirectQuote', ['name', 'district', 'moveto', 'link', 'movewhen', 'quotedate', 'size', 'movefrom', 'direct'])
     #   name = subject.split("Message from")[1].split("for")[0]
        name = self.subject.split(":")[1].split("is")[0]
        if " - " in self.subject:
            request_district = self.subject.split(" - ")[0]
        else:
            request_district = "Trek LA"
        stripped = soup.findAll("div")[7].stripped_strings
        stripped_list = [phrase for phrase in stripped]
        for i, string in enumerate(stripped_list):
            if "What is the size of your move" in string:
                size = stripped_list[i + 1]
            elif "zip code of your current location" in string:
                movefrom = stripped_list[i+1]
            elif "zip code at your destination" in string:
                moveto = stripped_list[i+1]
            elif "When do you want to move" in string:
                movewhen = stripped_list[i+1]
        
        direct_quote = DirectQuote(name, request_district, moveto, link, movewhen, None, size, movefrom, 'Direct')

        return direct_quote

    def parse_messages(self, messages, scraped_profiles):
        # messages is a list of dictionaries where each dictionary contains a message id.
        if messages:
            for msg in messages:
                # Get the message from its id
                txt = get_encoded_message(self.service, msg)
                # Get value of 'payload' from dictionary 'txt'
    
                if txt:
                    if txt.get("snippet") and "Attention, " in txt.get("snippet"):
                        continue
                    self.payload = txt['payload']
                    headers = self.payload['headers']
                    # Look for Subject and Sender Email in the headers
                    for d in headers:
                        if d['name'] == 'Subject':
                            self.subject = d['value']
                    self.relevant_parts = ["job for", "is requesting a quote"]
                    scraped_profiles = self.process_decoded_data(msg, scraped_profiles)
        return scraped_profiles
   
    def parse_nearby_job(self, soup, link):
        DirectQuote = namedtuple('DirectQuote', ['name', 'district', 'moveto', 'link', 'movewhen', 'quotedate', 'size', 'movefrom', 'direct'])

        stripped = ''.join([t.text for t in soup.findAll("td")]).replace("\n", "").strip()
        zip_avail = stripped.split("ZIP Code: ")[1]
        movefrom = zip_avail.split()[0]
        movewhen = stripped.split("ZIP Code: ")[1].split('Availability: ')[1].split("  ")[0]
        name = self.subject.split(" has a")[0]
        if "_wnBeUDshFbA3kh-MAqa6g" in link:
            request_district = "Trek LA"
        elif "ws6UJDDSo1cB8fc6f4A9BQ" in link:
            request_district = "Trek San Jose"
        elif "vKVDWIaMRSss3kZAkFbmBA" in link:
            request_district = "Trek Orange County"
        elif "6CV3T3cJwl9z3393c9VdVw" in link:
            request_district = "Trek Thousand Oaks"
        else:
            request_district = "Trek LA"
        quote = DirectQuote(name, request_district, None, link, movewhen, None, None, movefrom, 'Nearby')
        return quote