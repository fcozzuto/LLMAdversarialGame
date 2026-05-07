def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer resources that are closer to us than the opponent; otherwise just closest to us.
    best = None  # (score, rx, ry)
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        score = (ds - do, ds, rx, ry)
        if best is None or score < best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Avoid stepping onto immediate next positions that block us; keep tie-break deterministic.
        s1 = md(nx, ny, tx, ty)
        # Secondary: slightly prefer moves that also reduce distance to opponent (to contest safely).
        s2 = md(nx, ny, ox, oy)
        key = (s1, s2, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]