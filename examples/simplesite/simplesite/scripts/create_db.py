"""Create the application's database.

Run this once after installing the application::

    python -m simplesite.scripts.create_db development.ini
"""
import logging.config
import sys

from pyramid.paster import get_app
import transaction

import simplesite.models as models

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m simplesite.scripts.create_db INI_FILE")
    ini_file = sys.argv[1]
    logging.config.fileConfig(ini_file)
    log = logging.getLogger(__name__)
    app = get_app(ini_file, "SimpleDemo")
    #settings = app.registry.settings

    # Abort if any tables exist to prevent accidental overwriting
    for table in models.Base.metadata.sorted_tables:
        log.debug("checking if table '%s' exists", table.name)
        if table.exists():
            raise RuntimeError("database table '%s' exists" % table.name)

    # Create the tables
    models.Base.metadata.create_all()
    sess = models.Session()

    # Record 1
    #p = models.MyModel(id=1, name=u"Foo Bar")
    #sess.add(p)

    transaction.commit()

    

if __name__ == "__main__":  
    main()
