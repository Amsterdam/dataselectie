# Packages
from flask import Flask
from zelfbediening import adressen
from zelfbediening import health


def create_app(config=None):
        """
        An app factory
        Possible parameter config is a python path to the config object
        """
        app = Flask('geosearch')
        # Config
        if config:
            app.config.from_object(config)

        # Registering search blueprint
        app.register_blueprint(adressen.adressen)

        # Registering health blueprint
        app.register_blueprint(health.health)

        return app

