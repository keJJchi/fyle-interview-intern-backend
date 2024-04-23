from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.libs.assertions import assert_valid, assert_found
from core.libs.exceptions import FyleError

from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(grade_assignment_payload.id)
    if assignment is None:
        msg='NOT_FOUND'
        assert_found(False, msg)
        raise FyleError(status_code=404, message=msg)
    elif assignment and assignment.teacher_id == p.teacher_id:
            graded_assignment = Assignment.mark_grade(
                _id=grade_assignment_payload.id,
                grade=grade_assignment_payload.grade,
                auth_principal=p
            )
            db.session.commit()
            graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
            return APIResponse.respond(data=graded_assignment_dump)
    elif assignment.state in (AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.DRAFT):
            msg='only a draft assignment can be submitted'
            assert_valid(False, msg)
    raise FyleError(status_code=400, message={})