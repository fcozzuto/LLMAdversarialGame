def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    turns_left = int(observation.get("turns_remaining", 0) or 0)

    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(x, y, sx, sy)
        od = cheb(x, y, ox, oy)
        # prefer winning races; then closer to us; then earlier deadlines
        race_margin = od - sd  # positive means we are closer/equal than opponent
        # deadline heuristic: if both fit, favor earlier self; if only we fit, very good.
        self_fits = 1 if sd <= turns_left else 0
        opp_fits = 1 if od <= turns_left else 0
        fits_term = (2 if self_fits and not opp_fits else 0)
        deadline = sd if self_fits else (sd + turns_left * 2)
        key = (self_fits - opp_fits, race_margin + fits_term, -deadline, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis move if diagonal hits obstacle; deterministic fallback order.
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]

    return [dx, dy]