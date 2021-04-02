from automated_assessment_system.models import AssessmentAttempt, AssessmentAttemptState


def grader():
    """
    grader reads AssessmentAttempt in state of USER_DONE and grades the attempt.
    """
    done_attempts = AssessmentAttempt.objects.filter(
        state=AssessmentAttemptState.USER_DONE
    )
    print(f"processing {done_attempts.count()} number of done attempts")
    for done_attempt in done_attempts:
        total_points = 0
        assessment_responses = done_attempt.get_assessment_response()
        for assessment_response in assessment_responses:
            print(f"processing:  {assessment_response}")
            total_points += assessment_response.grade_question_selection()
        done_attempt.state_transition_to_graded(total_points)
