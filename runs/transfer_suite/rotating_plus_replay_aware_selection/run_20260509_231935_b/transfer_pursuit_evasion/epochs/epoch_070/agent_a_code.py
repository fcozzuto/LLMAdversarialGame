def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if res:
        target = min(res, key=lambda r: (d2((sx, sy), r), r[0], r[1]))
    else:
        target = (ox, oy)

    i_am_pursuer = True
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    if self_role:
        i_am_pursuer = ("pursuer" in self_role) or (("evader" not in self_role) and ("pursuer" not in opp_role))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nt = d2((nx, ny), target)
        no = d2((nx, ny), (ox, oy))
        # Favor moving toward target if pursuer; away if evader.
        score = (-nt if i_am_pursuer else nt) + (10 if (no > 0) else 0)
        if no == 0 and not i_am_pursuer:
            score -= 100000
        if no == 0 and i_am_pursuer:
            score += 100000
        score -= abs(nx - sx) + abs(ny - sy) * 0.01  # tiny tie-break
        if best is None or score > best:
            best = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]