def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = observation.get("self_role") or ""
    opponent_role = observation.get("opponent_role") or ""
    r = (self_role + " " + opponent_role).lower()
    self_is_pursuer = ("pursuer" in r) or ("pursuit" in r and "evader" not in r)
    # If role naming is ambiguous, infer from common convention:
    # pursuer usually gets points for capture; evader for survival -> if both mention neither, default to pursuer.
    if ("evader" in self_role.lower()) and ("pursuer" not in self_role.lower()):
        self_is_pursuer = False

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic tie-break: prefer diagonal, then right, then up, then stay.
    def move_pref(dx, dy):
        return (0 if dx != 0 and dy != 0 else 1, -dx, -dy)

    if not self_is_pursuer:
        # Choose a target corner that maximizes current distance from pursuer.
        target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
    else:
        target = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist(nx, ny, ox, oy)
        if self_is_pursuer:
            # Minimize distance to capture; add slight bias towards approaching the target corner of opponent's side if any.
            key = (d, abs(nx - ox) + abs(ny - oy), move_pref(dx, dy))
            want_min = True
        else:
            # Maximize distance from pursuer and also drift toward chosen corner.
            key = (-d, -dist(nx, ny, target[0], target[1]), move_pref(dx, dy))
            want_min = False

        if best_key is None:
            best_key = key
            best = (dx, dy)
        else:
            better = key < best_key if want_min else key < best_key
            if better:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]