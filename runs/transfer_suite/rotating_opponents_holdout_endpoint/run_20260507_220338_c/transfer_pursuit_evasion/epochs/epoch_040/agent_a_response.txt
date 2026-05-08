def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role_s) or ("chase" in role_s) or ("hunter" in role_s)
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s)
    if not (is_pursuer or is_evader):
        is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_clearance(x, y):
        m = 10
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in blocked:
                    m = min(m, dist2(nx, ny, ox, oy))
        return m

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        if is_pursuer:
            score = -d
            score += 0.01 * min_clearance(nx, ny)
        else:
            score = d
            # Slight preference to stay away from edges when many moves are blocked; deterministic tilt
            edge_pen = (0 if (1 <= nx < w - 1 and 1 <= ny < h - 1) else 1)
            score -= 0.05 * edge_pen
            score += 0.01 * min_clearance(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best