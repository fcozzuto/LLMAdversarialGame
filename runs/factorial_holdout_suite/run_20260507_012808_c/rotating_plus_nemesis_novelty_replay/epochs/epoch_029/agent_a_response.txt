def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # pick best target by "advantage over opponent" then proximity
    best_target = None
    best_key = None
    for t in resources:
        adv = md((ox, oy), t) - md((sx, sy), t)
        key = (adv, -md((sx, sy), t), -t[0], -t[1])
        if best_key is None or key > best_key:
            best_key = key
            best_target = t
    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    # choose best immediate move toward target, breaking ties by stealing advantage
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # deterministic tie-breaking: smaller dx then dy preference after scoring
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_d = md((nx, ny), (tx, ty))
        opp_d = md((ox, oy), (tx, ty))
        # Primary: increase advantage (opp_d - self_d). Secondary: reduce self_d.
        score = (opp_d - self_d, -self_d, -abs(nx - tx), -abs(ny - ty), -dx, -dy)
        scored.append((score, dx, dy))
    scored.sort(reverse=True)
    return [scored[0][1], scored[0][2]]