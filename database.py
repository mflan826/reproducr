from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Text, Boolean
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

class ArticleSummary(Base):
    __tablename__ = "article_summaries"
    __table_args__ = {'schema': 'daan_822'}
    pmid = Column(Text(), primary_key=True,unique=True,nullable=False)
    sort_date = Column(Date())

class ArticleDetailed(Base):
    __tablename__ = "article_detailed"
    __table_args__ = {'schema': 'daan_822'}
    pmid = Column(Text(), primary_key=True,unique=True,nullable=False)
    doi = Column(Text())
    data_available_details = Column(mutable_json_type(dbtype=JSON, nested=True))
    data_available = Column(Boolean())

Base.metadata.create_all(engine)

def create_connection() -> object:
    session = sessionmaker(engine)
    db_connection = session()
    return db_connection

def close_connection(con):
    con.close()
    return None

def write_data_summary(data,db_connection):
    for rec in data:
        db_connection.add(
            ArticleSummary(
                pmid=rec["pmid"],
                sort_date=rec['sortdate']
            )
        )
        db_connection.commit()
    return None

def write_data_detailed(data,db_connection):
    for rec in data:
        da_exists = False
        if len(rec[2]) > 0:
            da_exists = True

        db_connection.add(
            ArticleDetailed(
                pmid=rec[0],
                doi=rec[1],
                data_available_details=rec[2],
                data_available=da_exists # bool col just to make queries easier once it's in the db
            )
        )
        db_connection.commit()
    return None