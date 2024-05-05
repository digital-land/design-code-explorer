# design-code-explorer


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
