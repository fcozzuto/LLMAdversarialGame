def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in (observation.get(key) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set("unclaimed_cells")
    opp_t = to_set("opponent_territory")

    # Target selection (deterministic)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    targets = []
    if unclaimed:
        targets = list(unclaimed)
    elif opp_t:
        targets = list(opp_t)
    else:
        targets = [(cx, cy)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moves that reduce distance to best target; also avoid obstacles.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tiebreak = int(observation.get("turn_index") or 0) % 9

    best = None
    best_score = None
    for i, (dx, dy) in enumerate(dirs):
        if i != tiebreak and (i - tiebreak) % 9 != 0:
            pass
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Distance to closest target
        d = None
        for tr in targets:
            dd = manh((nx, ny), tr)
            if d is None or dd < d:
                d = dd
        d = d if d is not None else 10**9

        # Small deterministic preference: center, then unclaimed/opp territory
        center_pen = abs(nx - cx) + abs(ny - cy)
        in_unclaimed = 1 if (nx, ny) in unclaimed else 0
        in_opp = 1 if (nx, ny) in opp_t else 0
        score = (d, center_pen, -in_unclaimed, -in_opp, i)

        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # Guaranteed valid fallback: stay put
        return [0, 0]
    return best