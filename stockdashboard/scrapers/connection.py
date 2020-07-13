import requests 
from bs4 import BeautifulSoup as soup
from stockdashboard.scrapers.interfaces import EstablishConnectionInterface, ExtractDataInterface
import json 

class EstablishConnectionByRequest(EstablishConnectionInterface, ExtractDataInterface):
    """
    Connect to url using Request module 
    Implements:
        -EstablishConnection 
        -ExtractDataInterface
    """
    
    def __init__(self):
        self.current_session = requests.Session()
        self.response = None 
        self.html = None
        
    def connect(self, url, *, json_data=None, payload=None, headers=None, 
                credentials=None, query_string=None, timeout=30, stream=None):
        """
        Connect to webpage using request 'get'
        
        Parameters:
            url: The url of the page being requested 
            payload: The body of the request 
            headers: The headers data to pass with the request
            credentials: The credentials passed to the request for basic authentication
            query_string: The key/value pairs query string to pass with the request 
            timeout: amount of seconds to wait for connection and read
            stream: boolean, stream data, i.e. download media files 
            
        Returns:
            response, succesfull connection was made, False otherwise
        """
        try:
             self.response = self.current_session.get(url, json=json_data, data=payload, 
                                                      params=query_string, headers=headers, 
                                                      auth=credentials, timeout=timeout, 
                                                      stream=stream)
             self.response.raise_for_status()
             return self.response
        except requests.exceptions.HTTPError as e:
            print(f"\nEstablishConnectionByRequest.connect HTTP ERROR: {e}\n")
            return False
        except requests.exceptions.RequestException as e:
            print(f"\nEstablishConnectionByRequest.connect REQUEST ERROR: {e}\n")
            return False
        except Exception as e:
            print(f"\nEstablishConnectionByRequest.connect ERROR: {e}\n")
            return False
    
    def connect_post(self, url, *, json_data=None, payload=None, headers=None, 
                     credentials=None, query_string=None, timeout=30, stream=None):
        """
        Connect to webpage using request 'post'
        
        Parameters:
            url: The url of the page being requested 
            payload: The body of the request 
            headers: The headers data to pass with the request
            credentials: The credentials passed to the request for basic authentication
            query_string: The key/value pairs query string to pass with the request
            timeout: amount of seconds to wait for connection and read
            stream: boolean, stream data, i.e. download media files 
            
        Returns:
            response, succesfull connection was made, False otherwise
        """
        try:
             self.response = self.current_session.post(url, data=payload, json=json_data,
                                                       params=query_string, headers=headers, 
                                                       auth=credentials, timeout=timeout, 
                                                       stream=stream)
             self.response.raise_for_status()
             return self.response
        except requests.exceptions.HTTPError as e:
            print(f"EstablishConnectionByRequest.connect_post HTTP ERROR: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"EstablishConnectionByRequest.connect_post REQUEST ERROR: {e}")
            return False
        except Exception as e:
            print(f"EstablishConnectionByRequest.connect_post ERROR: {e}")
            return False
    
    def close(self):
        """
        Close the request session connection
        """
        self.current_session.close()
    
    def get_raw_data(self):
        """
        Get the html result of the response 
        
        Returns:
            self.html: the html data of the scraped resource
        """
        try:
            self.html = self.response.text
            return self.html
        except Exception as e:
            print(f"EstablishConnectionByRequest.get_raw_data ERROR: {e}")
            return None
    
    def _get_page_soup(self):
        """
        Get the lxml result of the response 
        
        Returns:
            page_soup: the ResultSet object of the scraped resource
        """
        try:
            page_soup = soup(self.get_raw_data(), 'lxml')
            return page_soup
        except Exception as e:
            print(f"EstablishConnectionByRequest._get_page_soup ERROR: {e}")
            return None

    def get_body(self):
        """
        Get the body data of the request 
        
        Returns:
            body: the html body of the webpage 
        """
        try:
            page_soup = self._get_page_soup()
            self.body = page_soup.body
            return self.body
        except Exception as e:
            print(f"EstablishConnectionByRequest.get_body ERROR: {e}")
            return None
    
    def get_element(self, element, attribute=None, value=None):
        """
        Get the element data of the request 
        
        Returns:
            element_data: the data from the element 
        """
        try:
            page_soup = self._get_page_soup()
            element_data = page_soup.find_all(element, {attribute: value})
            return element_data
        except Exception as e:
            print(f"EstablishConnectionByRequest.get_element ERROR: {e}")
            return None
    
    def get_json_data(self, raw_data=None):
        """
        Get the html data in json format 
        
        Returns:
            json_html: the data from the html in json format
        """
        
        if raw_data is None:
            raw_data = self.get_raw_data()
            
        try:
            json_data = json.loads(raw_data)
            return json_data
        except Exception as e:
            print(f"EstablishConnectionByRequest.get_json_data ERROR: {e}")
            return None
    
    
        






    