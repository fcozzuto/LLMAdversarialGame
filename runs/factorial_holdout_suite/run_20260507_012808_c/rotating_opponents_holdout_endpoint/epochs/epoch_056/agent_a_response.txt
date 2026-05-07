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

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick move that maximizes (opponent_dist - our_dist) for the best target.
    best = None
    for dx, dy, nx, ny in cand:
        my_pos = (nx, ny)
        score = -10**9
        for tx, ty in resources:
            opp_dist = d((ox, oy), (tx, ty))
            my_dist = d(my_pos, (tx, ty))
            # Favor ties and getting closer fast; slight preference for nearer overall.
            adv = opp_dist - my_dist
            tie_bonus = 0.5 if my_dist == opp_dist else 0.0
            closer = -0.05 * my_dist
            resource_bonus = 0.2 if my_dist == 0 else 0.0
            s = adv + tie_bonus + closer + resource_bonus
            if s > score:
                score = s
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then non-stay.
        tie = (dx == 0 and dy == 0, abs(dx), abs(dy))
        key = (score, -tie[0], -tie[1], -tie[2])
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]