def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_cells.append((rx, ry))
    if not res_cells:
        return [0, 0]

    def best_target_score(px, py):
        best = None
        for rx, ry in res_cells:
            sd = abs(px - rx) + abs(py - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Prefer resources we can reach sooner; otherwise deny by maximizing opponent lag.
            # Tie-break with smaller self distance and later lexicographic stability.
            score = (od - sd, -sd, rx, ry)
            if best is None or score > best[0]:
                best = (score, sd, rx, ry)
        return best[0]

    # Small lookahead: pick move maximizing target advantage.
    best_move = (None, None)
    best_score = (-10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine keeps us in place on invalid move
        sc = best_target_score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]