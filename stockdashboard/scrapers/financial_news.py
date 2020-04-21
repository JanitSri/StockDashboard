import concurrent.futures
from stockdashboard.scrapers.connection import EstablishConnectionByRequest


class FinancialNewsData():
    """
    Web scrape the current financial news from different sources
    """
    
    def __init__(self):
        self.connection = EstablishConnectionByRequest()
        
        
    def get_google_news(self, term):
        """
        Web scrape the current news from Google using the term 
        
        Parameters:
            term: The term to get news about
    
        Returns:
            news_links: The dictionary of news article headers and links 
        """
        
        try:
            if self.connection.connect(r'https://finance.yahoo.com/quote/{}'.format(term)):
                search = [term + " stock market"]
                title = [x.text for x in self.connection.get_element('h1')]
                
                if title:
                    search += title
                    
                seen_urls = list()
                news_links = dict()
                for s in search:
                    if self.connection.connect(r"https://www.google.com/search?hl=en&q={0}&tbm=nws&source=univ".format(s)):
                        data_header = self.connection.get_element('div','class','kCrYT')                        
                        for idx, data in enumerate(data_header):
                            data_text = data.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'})
                            header_text = term + " News"
                            
                            if data_text:
                                header_text = data_text.text
                            
                            link = data.find('a')
                            if link:
                                news_link = link['href'].lstrip('/url?q=').split('&')
                                
                            if len(news_link) > 0:
                                if news_link[0] not in seen_urls:
                                    seen_urls.append(news_link[0])
                                    header_text = header_text.replace('â\x80\x99', "'")
                                    news_links[header_text] = news_link[0]    
                return news_links
                
            return False
        except Exception as e:
            print("YAHOO FIN NEWS SCRAPE - GOOGLE:", e)
            return False

    def get_market_news(self):
        """
        Use the get_financial_news to get the market news 
        
        Returns:
            market_news: The dictionary of all the market news and links
        """
        try:
            markets_terms = ["DJIA","VIX","S&P/TSX","NASDAQ","RUSSELL 2000", "bonds"]
            
            market_news = dict()
            seen_market_news = set()
            finished = []
            
            with concurrent.futures.ThreadPoolExecutor() as executer:
                results = [executer.submit(self.get_google_news, terms) for terms in markets_terms]
            
                for f in concurrent.futures.as_completed(results):
                    finished.append(f.result())
            
            for news in finished:
                for key, value in news.items():
                    if key not in seen_market_news:
                        market_news[key] = news[key]
                        seen_market_news.add(key)
                        
            return market_news
        except Exception as e:
                print("YAHOO FIN NEWS SCRAPE - MARKET NEWS:", e)
                return False
    
    
    def get_marketwatch_news(self):
        """
        Web scrape the current news from Marketwatch
        
        Returns:
            market_news: The dictionary of the headlines and links from Marketwatch
        """
        try:
            if self.connection.connect(r'https://www.marketwatch.com/'):
                body = self.connection.get_body()
                found_links = [link.get('href') for link in body.find_all('a', {'class':'link'})]
                link_title = [x.text for x in body.find_all('a', {'class':'link'})] 
            
                market_news = dict()
                for link, title in zip(found_links, link_title):
                    if link and link.startswith(r'https://www.marketwatch.com/story/'):
                        title = title.strip()
                        title = ' '.join(title.split())
                        title = title.replace('â\x80\x99', "'")
                        market_news[title] = link
                
                return market_news
            return False
        except Exception as e:
            print("YAHOO FIN NEWS SCRAPE - MARKETWATCH NEWS:", e)
            return False
    
    
    def get_business_insider_news(self):
        """
        Web scrape the current news from Business Insider
        
        Returns:
            business_insider_news: The dictionary of the headlines and links from Business Insider
        """
        
        try:
            if self.connection.connect(r'http://markets.businessinsider.com/'):
                body = self.connection.get_body()
                found_links = [link.get('href') for link in body.find_all('a', {'class':'teaser-headline'})]
                found_headlines = [x.text for x in body.find_all('a', {'class':'teaser-headline'})]
                
                
                business_insider_news = dict()
                already_seen = list()
                for link, headline in zip(found_links, found_headlines):
                    
                    if headline not in already_seen:
                        link = 'http://markets.businessinsider.com{}'.format(link)
                        headline = headline.replace('â\x80\x99', "'")
                        business_insider_news[headline] = link
                        already_seen.append(headline)
                    
                return business_insider_news
                
            return False
        except Exception as e:
            print("YAHOO FIN NEWS SCRAPE - BUSINESS INSIDER NEWS:", e)
            return False
        
    
    def get_financial_post_news_helper(self, news_category):
        """
        Helper for the get_financial_post_news() to use threading 
        
        Parameters:
            news_category: The category to get the headlines and links from 
        
        Returns:
            news: The dictionary of the headlines and links from Financial Post
        """
        try:
            if self.connection.connect(r'https://business.financialpost.com/category/news/{}'.format(news_category)):
                body = self.connection.get_body()
                links = [x.find_all("a") for x in body.find_all('h4', {'class':'entry-title'})] 
                links2 = [x.find_all("a") for x in body.find_all('h2', {'class':'entry-title'})] 
            
                news = dict()    
                for link in links:
                    for href in link:
                        h4_text = href.text
                        h4_text = h4_text.replace('â\x80\x99', "'")
                        news[href.text] = href.get("href")
                
                for link in links2:
                    for href in link:
                        h2_text = href.text
                        h2_text = h2_text.replace('â\x80\x99', "'")
                        news[href.text] = href.get("href")
        
                return news  
            return False
        except Exception as e:
            print("YAHOO FIN NEWS SCRAPE - FINANCIAL POST NEWS:", e)
            return False
        
        
    
    def get_financial_post_news(self):
        """
        Web scrape the current news from Financial Post
        
        Returns:
            fin_post_news: The dictionary of all the market news from Financial Post
        """
        
        categories = ['', 'economy', 'fp-street', 'retail-marketing', 'telecom', 'transportation', 'real-estate', 'commodities']
        
        fin_post_news = {}
        with concurrent.futures.ThreadPoolExecutor() as executer:
            results = [executer.submit(self.get_financial_post_news_helper, category) for category in categories]
        
            for f in concurrent.futures.as_completed(results):
                fin_post_news.update(f.result())
        
        return fin_post_news
    
    def clean_up(self):
        self.connection.close()


