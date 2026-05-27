def choose_move(observation):
    # Deterministic, simple heuristic: move toward the opponent if present, else toward center.
    pos_self = observation.get("self_position", (0, 0))
    pos_opp = observation.get("opponent_position", None)

    x, y = pos_self if isinstance(pos_self, (list, tuple)) and len(pos_self) >= 2 else (0, 0)

    # default to stay
    dx = 0
    dy = 0

    # Try to move toward opponent if known
    if isinstance(pos_opp, (list, tuple)) and len(pos_opp) >= 2:
        ox, oy = pos_opp
        if ox > x:
            dx = 1
        elif ox < x:
            dx = -1
        else:
            dx = 0

        if oy > y:
            dy = 1
        elif oy < y:
            dy = -1
        else:
            dy = 0
    else:
        # center-seeking heuristic
        width = observation.get("grid_width", 0)
        height = observation.get("grid_height", 0)
        cx = width // 2
        cy = height // 2
        if x < cx:
            dx = 1
        elif x > cx:
            dx = -1
        else:
            dx = 0
        if y < cy:
            dy = 1
        elif y > cy:
            dy = -1
        else:
            dy = 0

    # Clamp to -1, 0, 1 and ensure integer
    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0

    return [dx, dy]
