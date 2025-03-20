# design-code-explorer

# ⚠️ Inactive

This application is no longer deployed anywhere. The data collected during it's use in a development plan timetable workshop has
been backed up and is available in [data/database_backup.dump](data/database_backup.dump)


## Getting started

Create a python virtualenv then run:

    make init

Create psql db called `design-codes`

```
createdb design-codes
```

Set up the required tables with the following

```
flask db upgrade
```

Run the app

    flask run
