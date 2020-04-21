import requests 
from bs4 import BeautifulSoup as soup
from stockdashboard.scrapers.interfaces import EstablishConnectionInterface, ExtractDataInterface

class EstablishConnectionByRequest(EstablishConnectionInterface, ExtractDataInterface):
    """
    Connect to url using Request module 
    Implements:
        -EstablishConnection 
        -ExtractDataInterface
    """
    
    def __init__(self):
        self.current_session = requests.Session()
        
    def connect(self, url, *, payload=None, headers=None, credentials=None, query_string=None):
        """
        Connect to webpage using request 'get'
        
        Parameters:
            url: The url of the page being requested 
            payload: The body of the request 
            headers: The headers data to pass with the request
            credentials: The credentials passed to the request for basic authentication
            query_string: The key/value pairs query string to pass with the request 
            
        Returns:
            Boolean, True if the succesfull connection was made, False otherwise
        """
        try:
             self.response = self.current_session.get(url, data=payload, params=query_string, headers=headers, auth=credentials)
             self.response.raise_for_status()
             return True
        except requests.exceptions.HTTPError as e:
            print(f"REQUEST HTTP ERROR: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"REQUEST ERROR: {e}")
            return False
        except Exception as e:
            print(f"OTHER ERROR: {e}")
            return False
    
    def close(self):
        """
        Close the request session connection
        """
        self.current_session.close()
    
    
    def get_raw_data(self):
        """
        Get the lxml result of the response 
        """
        try:
            html = self.response.text
            page_soup = soup(html, 'lxml')
            return page_soup
        except Exception as e:
            print(f"CONNECTION ERROR GET TEXT: {e}")
            return False


    def get_body(self):
        """
        Get the body data of the request 
        
        Returns:
            body: the html body of the webpage 
        """
        try:
            page_soup = self.get_raw_data()
            self.body = page_soup.body
            return self.body
        except Exception as e:
            print(f"CONNECTION ERROR GET RAW DATA: {e}")
            return False
    
    def get_element(self, element, attribute=None, value=None):
        """
        Get the element data of the request 
        
        Returns:
            element_data: the data from the element 
        """
        try:
            page_soup = self.get_raw_data()
            element_data = page_soup.find_all(element, {attribute: value})
            return element_data
        except Exception as e:
            print(f"CONNECTION ERROR GET RAW DATA: {e}")
            return False
    
    
        






    