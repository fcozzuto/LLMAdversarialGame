def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y = int(sx), int(sy)
    ex, ey = int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    target = None
    if res:
        if pursuer:
            target = min(res, key=lambda p: d2(x, y, p[0], p[1]))
        else:
            target = max(res, key=lambda p: d2(x, y, p[0], p[1]))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        dist_opp = d2(nx, ny, ex, ey)
        if target is not None:
            dist_t = d2(nx, ny, target[0], target[1])
            if pursuer:
                score = -(dist_opp + dist_t)
            else:
                score = (dist_opp - dist_t)
        else:
            score = -dist_opp if pursuer else dist_opp
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]