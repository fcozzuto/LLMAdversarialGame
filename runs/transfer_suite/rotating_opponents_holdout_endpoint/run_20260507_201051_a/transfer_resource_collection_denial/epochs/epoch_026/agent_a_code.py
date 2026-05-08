def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def parse_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return int(pos[0]), int(pos[1])
        return None

    targets = []
    for r in resources:
        p = parse_pos(r)
        if p:
            x, y = p
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        return [0, 0]

    def step_dist(ax, ay, bx, by):
        # With 8-direction moves (including diagonals), shortest steps is Chebyshev distance.
        dx = abs(bx - ax); dy = abs(by - ay)
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None

    for i, (tx, ty) in enumerate(targets):
        myd = step_dist(sx, sy, tx, ty)
        od = step_dist(ox, oy, tx, ty)
        adv = od - myd  # prefer positive advantage (we arrive not later)
        center_bias = - (abs(tx - cx) + abs(ty - cy))
        key = (-(adv), myd, -center_bias, i)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Avoid obvious immediate obstacle: if target step cell is blocked, try alternate axis moves deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs:
        cand = []
        cand.append((1 if tx > sx else -1 if tx < sx else 0, 0))
        cand.append((0, 1 if ty > sy else -1 if ty < sy else 0))
        cand.append((1 if tx > sx else -1 if tx < sx else 0, 1 if ty > sy else -1 if ty < sy else 0))
        cand.append((0, 0))
        for cdx, cdy in cand:
            nx2, ny2 = sx + cdx, sy + cdy
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obs:
                return [int(cdx), int(cdy)]

    return [int(dx), int(dy)]