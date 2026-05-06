def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay

    # Pick a resource we can arrive at no later than opponent, prefer largest lead; else deny closest-high-value.
    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        value = lead * 10 - ds
        if ds <= do:
            cand = (1, value, -rx, -ry)
        else:
            # denial: prefer cells opponent is close to and we are not too far from
            cand = (0, (do - ds) * 2 + (20 - do) - ds, -rx, -ry)
        if best is None or cand > best[0]:
            best = (cand, (rx, ry))

    _, (tx, ty) = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Greedy progress to target + opponent-aware pressure; discourage moving into obvious opponent approach.
        dist_to_t = md(nx, ny, tx, ty)
        dist_from_opp = md(nx, ny, ox, oy)
        opp_dist_to_t = md(ox, oy, tx, ty)

        # If opponent is already closer to target, we prioritize getting within "blocking" distance.
        blocking = 0
        if md(sx, sy, tx, ty) > md(ox, oy, tx, ty):
            blocking = 6 if dist_to_t <= opp_dist_to_t else -2

        score = (-dist_to_t * 10) + (dist_from_opp) + blocking

        # Deterministic tie-break: prefer lower dx, then lower dy, then staying.
        tie = (dx, dy)
        if best_score is None or (score, -tie[0], -tie[1]) > best_score:
            best_score = (score, -tie[0], -tie[1])
            best_move = [dx, dy]

    return best_move