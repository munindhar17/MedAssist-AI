from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from backend.database import Base


class Report(Base):

    __tablename__="reports"


    id=Column(
        Integer,
        primary_key=True,
        index=True
    )

    disease=Column(
        String
    )

    symptoms=Column(
        String
    )

    risk=Column(
        String
    )

    severity=Column(
        Integer
    )