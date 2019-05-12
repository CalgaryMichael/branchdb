# branchdb
A library that handles creating databases based off of your current git branch.

*Note*: this library is only targeted for development environments. This tool should never be used in a production environment.

### Why?

This library was inspired by database schema conflicts in Django when working across multiple git branches.
These scenarios can often be mitigated by unapplying migrations that exist on other git branches, but this highlights a bigger issue:
your git branch holds a certain state that your database is unable to replicate, creating scenarios where these states are out of sync.

branchdb attempts to fix these scenarios by allowing you to synchronize your git state with your database state.

### How?

Simple: by programmatically creating new databases based off of provided connection information.
These databases allow you to create new databases based off of [templates](https://www.postgresql.org/docs/9.5/manage-ag-templatedbs.html)
of previous databases, allowing for you to branch from a previous state — similar to creating new branches in git.

You can then utilize these databases by calling this library to get the "active" database.

Example for a django project:
```python
# in settings.py
from branchdb.database import get_current_database
...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_current_database(),
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': 5432
    }
}
```

### Support

Current implementation supports the following databases in py2.7, py3.6, and py3.7:
* PostgreSQL >= 9.4

This library is also extensible, allowing you to create support for databases not listed by using the `Engine` class.

### Setup

Each of your projects needs to be initialized in order to use this tool.
To initialize your project, run the following command:
```bash
branchdb init {starting database}
```

After you've run this command, go into the `.branchdb/settings.py` file to set up your database connections.

Once you have done this, it is advised that you create a database for your master branch by running the following:
```bash
branchdb create --branch master
```
