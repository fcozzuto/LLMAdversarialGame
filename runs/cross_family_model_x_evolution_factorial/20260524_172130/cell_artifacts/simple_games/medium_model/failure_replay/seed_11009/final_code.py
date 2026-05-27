def choose_move(observation):
    # Defensive access
    mode = observation.get("mode", "")
    pose = observation.get("pose", {}) or {}
    x = pose.get("x", 0)
    y = pose.get("y", 0)

    # Ensure numeric
    if not isinstance(x, (int, float)):
        x = 0
    if not isinstance(y, (int, float)):
        y = 0

    dx = 0
    dy = 0

    # Move toward origin when coordinates are informative
    if x > 0:
        dx = -1
    elif x < 0:
        dx = 1

    if y > 0:
        dy = -1
    elif y < 0:
        dy = 1

    # If no information or already at origin, apply mode-based fallback
    if dx == 0 and dy == 0:
        if mode == "resource_collection":
            dx, dy = (1, 0) if (isinstance(x, (int, float)) and x <= 0) else (-1, 0)
        elif mode == "pursuit_evasion":
            dy = 1 if y <= 0 else -1
            dx = 0
        elif mode == "territory_control":
            dx, dy = (-1, 0) if x >= 0 else (1, 0)
            # small downward bias to help territorial work
            dy = -1
        else:
            dx, dy = (0, 0)

    # Clamp to valid range
    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0

    return [dx, dy]
