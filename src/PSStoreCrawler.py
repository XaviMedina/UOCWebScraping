import urllib2
import robotparser
import urlparse
import time
from Game import Game
from bs4 import BeautifulSoup
import pandas as pd

class PSStoreCrawler:

    base_url = ""
    visited_urls = []
    urls_to_visit = []
    games_dataset = []
    checkpoint_value = 200
    categories_to_crawl = []

    def __init__(self, base_url, categories_to_crawl, checkpoint_value=200):
        self.base_url = base_url
        self.categories_to_crawl = categories_to_crawl
        self.checkpoint_value = checkpoint_value

    def init_robot_parser(self, url):
        rp = robotparser.RobotFileParser()
        rp.set_url(urlparse.urljoin(url, "robots.txt"))
        rp.read()
        return rp

    def obtain_game_info(self, soup):
        game = Game()
        game.name = soup.find("h2", {'class':'pdp__title'}).get_text()
        provider_info = soup.findAll("h5", {'class': 'provider-info__text'})
        if provider_info is not None:
            if len(provider_info) > 1:
                game.provider = provider_info[0].get_text()
                release_date = provider_info[1].findAll('span')
                if release_date is not None and len(release_date) > 1:
                    game.release_date = release_date[1].get_text().split('Lanzado')[0]
            else:
                if "Lanzado" in provider_info:
                    game.release_date = provider_info[0].findAll('span')[1].get_text().split('Lanzado')[1]
                else:
                    game.provider = provider_info[0].get_text()
        platforms = soup.find('div', {'class': 'playable-on__button-set'}).find_all('a')
        if platforms is not None:
            platform_value = ""
            for platform in platforms:
                if platform_value != "":
                    platform_value = platform_value + ", " + platform.get_text()
                else:
                    platform_value = platform.get_text()
            game.platform = platform_value
        price = soup.find("h3", {'class': 'price-display__price'})
        if price is not None:
            game.price = price.get_text()
        left_menu = soup.find("div", {'class': 'tech-specs__pivot-menus'})
        if left_menu is not None:
            genres = left_menu.find('ul')
            if genres is not None:
                for genre in genres.findAll('li'):
                    genres_value = ""
                    if genres_value != "":
                        genres_value = genres_value + genre.get_text()
                    else:
                        genres_value = genre.get_text()
                    game.genres = genres_value
            items = left_menu.findAll('div', {'class': 'tech-specs__menu-items'})
            if items is not None:
                for item in items:
                    if "GB" in item.get_text():
                        game.size = item.get_text()
        plus_exclusive = soup.find('h3', {'class': 'price-display__price--is-plus-exclusive'})
        if plus_exclusive is not None:
            game.price = plus_exclusive.get_text()
            game.is_plus_exclusive = "Plus exclusive"
        self.games_dataset.append(game)

    def parse_page(self, html):
        soup = BeautifulSoup(html, 'lxml')
        soup.encode("utf-8")
        pagination = soup.find('div', {'class': 'paginator-control__container'})
        if pagination is not None:
            next_page = soup.find('a', {'class': 'paginator-control__next paginator-control__arrow-navigation internal-app-link ember-view'})
            if next_page is not None:
                self.urls_to_visit.append(urlparse.urljoin(self.base_url, next_page['href']))
            urls = soup.findAll('div', {'class': 'grid-cell grid-cell--game-related'})
            if urls is not None:
                for url in urls:
                    self.urls_to_visit.append(urlparse.urljoin(self.base_url,url.a['href']))
        else:
            self.obtain_game_info(soup)

    def scrap_web_content(self, html, url, user_agent):
        if html is not None:
            self.parse_page(html)
        else:
            print "Html is empty"
            return


    def download(self,url, robot_parser, user_agent='uocwsp', num_retries=10):
        if url not in self.visited_urls:
            print 'Downloading:', url
            headers = {'User-agent': user_agent}
            request = urllib2.Request(urlparse.urljoin(url, "?activeTab=dependencies"), headers=headers)
            try:
                if robot_parser.can_fetch(user_agent, url):
                    html = urllib2.urlopen(request).read()
                    self.visited_urls.append(url)
                    self.scrap_web_content(html, url, user_agent)
                else:
                    print 'Url blocked by robots.txt'
            except urllib2.HTTPError as e:
                print e.code
                print e.headers
                if num_retries > 0:
                    if hasattr(e, 'code') and 500 <= e.code < 600:
                        return self.download(url, robot_parser, user_agent, num_retries - 1)
                    if e.code == 429:
                        time.sleep(60)
                        return self.download(url, robot_parser, user_agent, num_retries - 1)
            except urllib2.URLError as e:
                print 'Download error: ', e.reason
                print 'Error header: ', e.headers
                if num_retries > 0:
                    if hasattr(e, 'code') and 500 <= e.code < 600:
                        return self.download(url, robot_parser, user_agent, num_retries-1)
            self.urls_to_visit.remove(url)
        else:
            self.urls_to_visit.remove(url)
            return


    def crawl_psstore(self):
        print "Starting to crawl"
        rp = self.init_robot_parser(self.base_url)
        for category in self.categories_to_crawl:
            self.urls_to_visit.append(urlparse.urljoin(self.base_url, category))
            while len(self.urls_to_visit) > 0:
                if len(self.games_dataset) == self.checkpoint_value:
                    self.generate_csv(self.games_dataset)
                    self.checkpoint_value = self.checkpoint_value + 200
                self.download(self.urls_to_visit[0], rp)
        self.generate_csv(self.games_dataset)

    def generate_csv(self, data):
        print "Generating CSV"
        df = pd.DataFrame.from_records([package.to_dict() for package in data])
        df.to_csv("../csv/dataset.csv", index=False, columns=['name','provider','release_date','genres','price','platform','size','is_plus_exclusive'], sep = ';', encoding = 'utf-8')




