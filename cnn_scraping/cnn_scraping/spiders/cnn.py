import scrapy
from ..items import CnnScrapingItem

class Quote(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://www.cnn.com",
    ]

    def parse(self, response):

        #websites = response.xpath("//li[@class='sc-chPdSV HrDCu']/a/@href").extract()
        websites = response.xpath("//li[@class='sc-chPdSV jUoWJl']/a/@href").extract()
        required_categories=["/us","/world","/politics","/business","/health","/travel"]
        websites=[i for i in websites if i in required_categories]
        for url in websites:
            if url is not None:
                category=url[1:]
                url = response.urljoin(url)
                yield response.follow(url, callback=self.parse_section,meta={'category': category})

    def parse_section(self, response):
        article_link = response.xpath("//h3[@class='cd__headline']/a/@href").extract()
        category = response.request.meta['category']
        for articles in article_link:
            if articles is not None:
                artciles = response.urljoin(articles)
                yield response.follow(articles, callback=self.parse_article, meta={'category':category})

    def parse_article(self, response):

        items = CnnScrapingItem()
        article_content = response.xpath("//div[@class='zn-body__paragraph']/text()").extract()
        category = response.request.meta['category']
        if article_content!=[]:
            url = response.url
            title = response.xpath("//h1[@class='pg-headline']/text()").extract_first()  #something wrong
            #article_content = response.xpath("//div[@class='zn-body__paragraph']/text()").extract()
            article_content2=response.xpath("//div[@class='zn-body__paragraph speakable']/text()").extract()
            article_content_all=article_content+article_content2
            article_content_join = " ".join(article_content_all)
            author1 = response.xpath("//span[@class='metadata__byline__author']/text()").extract()
            author2 = response.xpath("//span[@class='metadata__byline__author']/a/text()").extract() #if the author contains a URL
            if author2 != []:
                author=author2
            else:
                author=author1
            date = response.xpath("//p[@class='update-time']/text()").extract_first()

            items['url']=url
            items['title'] = title
            items['article'] = article_content_join
            items['author'] = author
            items['date'] = date
            items['category']=category

            yield items

# scrapy crawl quotes -o cnn_news.csv