def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]),
                                             -dist2(ox, oy, p[0], p[1]),
                                             p[0], p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best: best = key; best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    best_cell = None
    best_key = None
    for rx, ry in resources:
        self_d = dist2(sx, sy, rx, ry)
        opp_d = dist2(ox, oy, rx, ry)
        # Prefer resources opponent is farther from; break ties by reaching sooner.
        key = (-(opp_d - self_d), self_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (rx, ry)

    bx, by = best_cell
    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue

        # If we step onto a resource, strongly prioritize.
        on_res = (nx, ny) in set(tuple(p) for p in resources)
        self_after = dist2(nx, ny, bx, by)

        # Also discourage moves that allow opponent to be closer to the next best resource.
        # Approximate by comparing distance to our target and opponent distance to it.
        opp_to_target = dist2(ox, oy, bx, by)

        # Score: maximize chance to beat; tie-break by being closer to target.
        key = (0 if on_res else 1,
               self_after - opp_to_target,
               self_after, nx, ny)

        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move if best is not None else [0, 0]