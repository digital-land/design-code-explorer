from flask.cli import AppGroup

data_cli = AppGroup("data")


@data_cli.command("load")
def load_data():
    print("Loading data")
