def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    my_corner = min(corners, key=lambda c: abs(sx - c[0]) + abs(sy - c[1]))

    def manhattan(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    best = None
    best_val = None
    for rx, ry in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        # Race term (minimax-ish): reward where opponent is farther, punish where opponent is closer.
        race = (od - sd)
        corner_prog = -manhattan(rx, ry, my_corner[0], my_corner[1])
        # Small penalty for long travel to avoid getting lured into worse races.
        val = race * 100 - sd * 5 + corner_prog
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer direct diagonal/step toward target if not blocked; otherwise try axis alternatives deterministically.
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for cdx, cdy in cand:
        nx, ny = sx + cdx, sy + cdy
        if ok(nx, ny):
            return [int(cdx), int(cdy)]
    return [0, 0]