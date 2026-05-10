def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    if (sx, sy) in set(tuple(r) for r in resources if r and len(r) >= 2):
        return [0, 0]

    best_target = None
    best_score = None

    # Score targets by (opp_advantage - our_distance) and also prefer far columns from opponent (vs row sweeps).
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx = int(r[0]); ry = int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        if self_d == 0:
            return [0, 0]
        opp_adv = opp_d - self_d  # positive if we're closer
        # Prefer targets where opponent is relatively worse, and discourage letting them contest in similar x.
        score = (opp_adv * 10) - self_d - (abs(rx - ox) / 2.0)
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If blocked, try alternate deterministic step towards target along available directions.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(cdx), int(cdy)]
    return [0, 0]