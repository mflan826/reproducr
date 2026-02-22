from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy import Column, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy_json import mutable_json_type
import os
from dotenv import load_dotenv

load_dotenv()

url = URL.create(
    drivername='postgresql',
    username=os.getenv('USER'),
    password=os.getenv('PW'),
    host=os.getenv('HOST'),
    database=os.getenv('DB_NAME')
)

engine = create_engine(url, poolclass=NullPool, connect_args={'sslmode': os.getenv('SSL_MODE')})

Base = declarative_base()

class ArticleDetailed(Base):
    __tablename__ = "article_detailed"
    __table_args__ = {'schema': 'daan_822'}
    pmid = Column(Text(), primary_key=True,unique=True,nullable=False)
    doi = Column(Text())
    article_type = Column(Text())
    article_title = Column(Text())
    pub_date = Column(Text())
    keywords = Column(mutable_json_type(dbtype=JSON, nested=True))
    funding = Column(mutable_json_type(dbtype=JSON, nested=True))
    data_available_details = Column(mutable_json_type(dbtype=JSON, nested=True))
    data_available = Column(Boolean())
    code_available_details = Column(mutable_json_type(dbtype=JSON, nested=True))
    code_available = Column(Boolean())

Base.metadata.create_all(engine)

def create_connection() -> object:
    session = sessionmaker(engine)
    db_connection = session()
    return db_connection

def close_connection(con):
    con.close()
    return None

def write_data_detailed(data,db_connection):
        for rec in data:
            if rec["pmid"] is not None:
                db_connection.add(
                    ArticleDetailed(
                        pmid=rec["pmid"],
                        doi=rec["doi"],
                        article_type=rec["article_type"],
                        article_title=rec["article_title"],
                        pub_date=rec["pub_date"],
                        keywords=rec["keywords"],
                        funding=rec["funding"],
                        data_available_details=rec["data_availability"],
                        data_available=len(rec["data_availability"]) > 0,
                        code_available_details=rec["code_availability"],
                        code_available=len(rec["code_availability"]) > 0,
                    )
                )
                db_connection.commit()