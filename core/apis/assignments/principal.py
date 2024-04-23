from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.libs.assertions import assert_valid

from .schema import AssignmentSchema, AssignmentGradeSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(_):
    """Returns all list of assignments"""
    principal_assignments = Assignment.get_assignments_by_principal()
    principal_assignments_dump = AssignmentSchema().dump(principal_assignments, many=True)
    return APIResponse.respond(data=principal_assignments_dump)

@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p, incoming_payload):
    """Re-grade an assignment"""
    regrade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(regrade_assignment_payload.id)

    if getattr(assignment,"state", None) in (AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED):
        regraded_assignment = Assignment.mark_grade(
            _id=regrade_assignment_payload.id,
            grade=regrade_assignment_payload.grade,
            auth_principal=p
        )
        db.session.commit()
        regraded_assignment_dump = AssignmentSchema().dump(regraded_assignment)
        return APIResponse.respond(data=regraded_assignment_dump)
    msg = "Assignment is in Draft state"
    assert_valid(False, msg)
