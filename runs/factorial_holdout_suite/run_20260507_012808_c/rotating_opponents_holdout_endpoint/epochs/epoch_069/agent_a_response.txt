def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    t = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        delta = opp_d - self_d  # prefer resources where we are closer
        # If losing, prioritize "less bad" and also mildly away from opponent to reduce contestability
        opp_close_bonus = -(abs(rx - ox) + abs(ry - oy))
        key = (delta, opp_close_bonus, -self_d, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = sign(rx - sx)
    dy = sign(ry - sy)

    # Deterministic anti-linearity: sometimes move along one axis only to vary path
    if dx != 0 and dy != 0:
        if (t + rx * 3 + ry * 5) % 2 == 0:
            if (t + rx + sy) % 3 == 0:
                dy = 0
            else:
                dx = 0

    nx, ny = sx + dx, sy + dy
    if (0 <= nx < w and 0 <= ny < h) and (nx, ny) not in obstacles:
        return [dx, dy]

    # If blocked, try axis move (deterministic) then stay
    for adx, ady in ((dx, 0), (0, dy), (0, 0)):
        nx, ny = sx + adx, sy + ady
        if (0 <= nx < w and 0 <= ny < h) and (nx, ny) not in obstacles:
            return [adx, ady]
    return [0, 0]