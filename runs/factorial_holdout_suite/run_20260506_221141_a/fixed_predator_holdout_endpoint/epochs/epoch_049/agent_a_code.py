def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_t = None
    best_td = 10**18
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                dd = d((sx, sy), (x, y))
                if dd < best_td:
                    best_td = dd
                    best_t = (x, y)

    tx, ty = best_t if best_t is not None else (ox, oy)

    avoid = None
    if d((sx, sy), (ox, oy)) <= 2:
        avoid = (ox, oy)

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                cand_ok = True
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
                cand_ok = inb(nx, ny) and (nx, ny) not in obs and (avoid is None or (nx, ny) != avoid)
            if not cand_ok:
                continue
            dist_to_target = d((nx, ny), (tx, ty))
            dist_to_opp = d((nx, ny), (ox, oy))
            threat = 0
            if d((nx, ny), (ox, oy)) <= 1:
                threat = 1000
            score = (-10 * dist_to_target) + (2 * dist_to_opp) - threat
            if not cand_ok:
                continue
            if (dx, dy) == (0, 0):
                score -= 0.1
            if 0 <= nx < w and 0 <= ny < h:
                score += 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move