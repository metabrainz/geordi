from flask.ext.script import Manager
from geordi import create_app

manager = Manager(create_app())
if __name__ == "__main__":
    manager.run()
