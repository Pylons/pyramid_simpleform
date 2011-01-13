import logging

import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm
import transaction

log = logging.getLogger(__name__)

Base = psa.get_base()
Session = psa.get_session()


class MyModel(Base):
    __tablename__ = 'models'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), nullable=False)
    value = sa.Column(sa.Integer, nullable=False)


def initialize_sql(engine):

    Base.metadata.bind = engine
    Base.metadata.create_all()
