import abc 

class ExtractDataInterface(metaclass=abc.ABCMeta):
    """
    Interface to extract and clean data from web pages 
    """
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_raw_data') and 
                callable(subclass.load_data_source) or 
                NotImplemented)
    
    @abc.abstractmethod
    def get_raw_data(self):
        """get the data in raw format"""
        raise NotImplementedError

    
class EstablishConnectionInterface(metaclass=abc.ABCMeta):
    """
    Interface to connect to various third parties 
    """
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'connect') and 
                callable(subclass.load_data_source) and 
                hasattr(subclass, 'close') and 
                callable(subclass.extract_text) or 
                NotImplemented)
    
    @abc.abstractmethod
    def connect(self, *, url=None, payload=None, headers=None, credentials=None):
        """make connection to third party"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def close(self):
        """close connection to third party"""
        raise NotImplementedError
        
        
        
        
        
        
        
        
        
        
        