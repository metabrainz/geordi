from flask import render_template


def init_error_handlers(app):

    @app.errorhandler(404)
    def not_found_handler(error):
        return render_template('errors/404.html', error=error), 404
