from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, Integer

class CustomBase:
    @declared_attr

    # Now automatically each model will have table name which would be the filename in lowercase
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # Each table will also have an id
    id = Column(Integer, primary_key=True, index=True)

Base = declarative_base(cls=CustomBase)