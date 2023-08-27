import os
from dotenv import load_dotenv
import time
from customerio import APIClient, SendEmailRequest, CustomerIOException

class CommonlyCustomerio():

    def __init__(self, api_key):
        self.api_key = api_key
        # Create a ChromeOptions object
        pass
    
    def send_match_message(self, names, venue_name, venue_address, date, time, group_size, emails, groupme):
        print(self.api_key)
        api = APIClient(self.api_key)
        data = {
            'group_size': group_size,
            'venue': venue_name,
            'date': date,
            'time': time,
            'address': venue_address,
            'group_names': names,
            'groupme': groupme
        }
        request = SendEmailRequest(
            transactional_message_id="3",
            message_data=data,
            identifiers={
                "id": "none"
            },
            to=emails,
            subject = "Commonly - You've been Matched " + data['date'] + " @ " + data['time']
        )
        try:
            api.send_email(request)
        except CustomerIOException as e:
            print("error: ", e)

if __name__ == "__main__":
    load_dotenv()
    commonly_customerio = CommonlyCustomerio()
    commonly_customerio.send_match_message()