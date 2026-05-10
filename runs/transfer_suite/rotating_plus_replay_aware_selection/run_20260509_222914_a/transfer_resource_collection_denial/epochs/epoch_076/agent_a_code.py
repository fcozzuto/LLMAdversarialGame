def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def best_target_from(x, y):
        best = None
        for tx, ty in resources:
            sd = man(x, y, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer targets we can beat; otherwise minimize opp lead.
            lead = od - sd  # higher is better
            # Secondary: prefer shorter self distance; then closer to opp (to potentially deny later).
            cand = (lead, -sd, -od)
            if best is None or cand > best:
                best = cand
        return best

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sc = best_target_from(nx, ny)
        if sc is None:
            continue
        # Encourage moving toward the chosen target by slight penalty on step distance moved when tied.
        # (Manhattan between current and next is deterministic and small.)
        tie = (sc, -man(sx, sy, nx, ny))
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]