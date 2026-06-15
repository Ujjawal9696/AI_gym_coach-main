import numpy as np

# Standard MediaPipe Pose landmark indices
NOSE = 0
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_ELBOW, RIGHT_ELBOW = 13, 14
LEFT_WRIST, RIGHT_WRIST = 15, 16
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28


def _angle(a, b, c):
    """Angle at point b, formed by points a-b-c, in degrees."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))


def _vertical_angle(a, b):
    """Angle of segment a-b from vertical axis, in degrees."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    vec = b - a
    vertical = np.array([0, 1])
    cos_angle = np.dot(vec, vertical) / (np.linalg.norm(vec) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))


def _score_squats(lm):
    score = 100
    feedbacks = []

    knee_angle = _angle(lm[LEFT_HIP], lm[LEFT_KNEE], lm[LEFT_ANKLE])
    hip_angle = _angle(lm[LEFT_SHOULDER], lm[LEFT_HIP], lm[LEFT_KNEE])
    back_angle = _vertical_angle(lm[LEFT_SHOULDER], lm[LEFT_HIP])

    if knee_angle > 160:
        feedbacks.append("Bend your knees more for proper squat depth")
        score -= 20
    elif knee_angle < 70:
        feedbacks.append("You're squatting too deep, watch your knees")
        score -= 10

    if back_angle > 45:
        feedbacks.append("Keep your back straighter, avoid leaning forward")
        score -= 25

    if hip_angle < 60:
        feedbacks.append("Push your hips back more")
        score -= 10

    return score, feedbacks


def _score_pushups(lm):
    score = 100
    feedbacks = []

    elbow_angle = _angle(lm[LEFT_SHOULDER], lm[LEFT_ELBOW], lm[LEFT_WRIST])
    body_line_angle = _angle(lm[LEFT_SHOULDER], lm[LEFT_HIP], lm[LEFT_ANKLE])

    if body_line_angle < 160:
        feedbacks.append("Keep your body in a straight line, don't sag your hips")
        score -= 25

    if elbow_angle > 170:
        feedbacks.append("Lower yourself more for full range of motion")
        score -= 10

    return score, feedbacks


def _score_biceps_curl(lm):
    score = 100
    feedbacks = []

    elbow_angle = _angle(lm[LEFT_SHOULDER], lm[LEFT_ELBOW], lm[LEFT_WRIST])
    shoulder_movement = _vertical_angle(lm[LEFT_HIP], lm[LEFT_SHOULDER])

    if shoulder_movement > 15:
        feedbacks.append("Avoid swinging your shoulders, keep upper arm still")
        score -= 25

    if elbow_angle < 30:
        feedbacks.append("Great curl range!")
    elif elbow_angle > 170:
        feedbacks.append("Don't fully lock out, keep slight tension")
        score -= 5

    return score, feedbacks


def _score_shoulder_press(lm):
    score = 100
    feedbacks = []

    elbow_angle = _angle(lm[LEFT_SHOULDER], lm[LEFT_ELBOW], lm[LEFT_WRIST])
    back_angle = _vertical_angle(lm[LEFT_SHOULDER], lm[LEFT_HIP])

    if back_angle > 20:
        feedbacks.append("Avoid arching your back during the press")
        score -= 25

    if elbow_angle < 150:
        feedbacks.append("Extend your arms fully overhead")
        score -= 10

    return score, feedbacks


def _score_lunges(lm):
    score = 100
    feedbacks = []

    front_knee_angle = _angle(lm[LEFT_HIP], lm[LEFT_KNEE], lm[LEFT_ANKLE])
    torso_angle = _vertical_angle(lm[LEFT_SHOULDER], lm[LEFT_HIP])

    if front_knee_angle < 70:
        feedbacks.append("Don't let your front knee go too far past your toes")
        score -= 15

    if torso_angle > 20:
        feedbacks.append("Keep your torso upright")
        score -= 20

    return score, feedbacks


_SCORERS = {
    "Squats": _score_squats,
    "Push-ups": _score_pushups,
    "Biceps Curls (Dumbbell)": _score_biceps_curl,
    "Shoulder Press": _score_shoulder_press,
    "Lunges": _score_lunges,
}


def get_form_score(ex_type, landmarks):
    """
    Returns (score: int, feedbacks: list[str]) for the given exercise type
    and a list of MediaPipe pose landmarks.
    """
    scorer = _SCORERS.get(ex_type)
    if scorer is None:
        return 100, []

    try:
        score, feedbacks = scorer(landmarks)
    except (IndexError, AttributeError):
        return 0, ["Pose not fully visible"]

    score = int(max(0, min(100, score)))
    return score, feedbacks