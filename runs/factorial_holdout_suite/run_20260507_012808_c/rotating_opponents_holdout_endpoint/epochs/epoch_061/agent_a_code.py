def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    yield (0, 0)
                break
            break

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    opp_best = min(cheb((ox, oy), r) for r in resources)

    best = cand[0]
    best_key = (-10**18, 10**18, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        self_best = min(cheb((nx, ny), r) for r in resources)
        lead = opp_best - self_best
        # tie-break: when close, prefer smaller self_best; also nudge toward staying away from opp if tie
        opp_after = min(cheb((ox, oy), r) for r in resources)
        away = -cheb((nx, ny), (ox, oy))
        key = (lead, -self_best, away)
        if key > best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]