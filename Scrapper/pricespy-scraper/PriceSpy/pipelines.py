# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2


class PricespyPipeline:

    def __init__(self, postgres_settings):
        self.postgres_settings = postgres_settings

        # ## Create/Connect to database
        # self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        #
        # ## Create cursor, used to execute commands
        # self.cur = self.connection.cursor()
        #
        # ## Create quotes table if none exists
        # self.cur.execute("""
        #        CREATE TABLE IF NOT EXISTS product
        #        (
        #            id       serial
        #                primary key,
        #            name     varchar(255),
        #            model    varchar(255),
        #            link     varchar(255),
        #            price    integer,
        #            discount integer,
        #            brand    varchar(255),
        #            category varchar(255),
        #            specs    varchar(2000)
        #        )
        #        """)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        postgres_settings = {
            'host': settings.get('POSTGRES_HOST', 'ep-holy-surf-a2elkdep.eu-central-1.aws.neon.tech'),
            'port': settings.get('POSTGRES_PORT', 5432),
            'database': settings.get('POSTGRES_DB', 'DIALDIVER'),
            'user': settings.get('POSTGRES_USER', 'killercoseru'),
            'password': settings.get('POSTGRES_PASSWORD', 'SCFt4ja2ougp'),
        }
        return cls(postgres_settings)

    # def __init__(self):
    #     ## Connection Details
    #     hostname = 'localhost'
    #     username = 'postgres'
    #     password = 'iceage'  # your password
    #     database = 'price_spy'
    #
    #     ## Create/Connect to database
    #     self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    #
    #     ## Create cursor, used to execute commands
    #     self.cur = self.connection.cursor()
    #
    #     ## Create quotes table if none exists
    #     self.cur.execute("""
    #     CREATE TABLE IF NOT EXISTS product
    #     (
    #         id       serial
    #             primary key,
    #         name     varchar(255),
    #         model    varchar(255),
    #         link     varchar(255),
    #         price    integer,
    #         discount integer,
    #         brand    varchar(255),
    #         category varchar(255),
    #         specs    varchar(2000)
    #     )
    #     """)

    def process_item(self, item, spider):
        ## Define insert statement
        print("HAHAHAHAHAHA")
        insert_sql = """ 
            insert into product (name, model, link,price,discount, brand,category, specs, new, shop) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        data = (
            item["name"],
            item["model"],
            item["link"],
            item["price"],
            item["discount"],
            item["brand"].capitalize(),
            item["category"],
            item["specs"],
            item["new"],
            item["shop"]
        )

        try:
            self.cursor.execute(insert_sql, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            spider.log(f"Error inserting data: {str(e)}", level=logging.ERROR)
        return item

    def open_spider(self, spider):
        self.conn = psycopg2.connect(**self.postgres_settings)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
    # def close_spider(self, spider):
    #     ## Close cursor & connection to database
    #     self.cur.close()
    #     self.connection.close()
