from flask import jsonify
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources, principal_assignments_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException

from sqlalchemy.exc import IntegrityError

app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')
app.register_blueprint(principal_assignments_resources, url_prefix='/principal')


@app.route('/')
def ready():
    return jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

@app.errorhandler(Exception)
def handle_error(err):
    error_responses = {
        FyleError: lambda e: (
            jsonify(error=e.__class__.__name__, message=e.message), e.status_code
        ),
        ValidationError: lambda e: (
            jsonify(error=e.__class__.__name__, message=e.messages), 400
        ),
        IntegrityError: lambda e: (
            jsonify(error=e.__class__.__name__, message=str(e.orig)), 400
        ),
        HTTPException: lambda e: (
            jsonify(error=e.__class__.__name__, message=str(e)), e.code
        )
    }

    for error_type, response_func in error_responses.items():
        if isinstance(err, error_type):
            return response_func(err)
