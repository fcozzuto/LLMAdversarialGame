def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    targets = []
    for k in ("resources", "unclaimed_cells"):
        cells = observation.get(k) or []
        for p in cells:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                    targets.append((x, y))
        if targets:
            break

    opp_cells = []
    ot = observation.get("opponent_territory") or []
    for p in ot:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                opp_cells.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        targets = opp_cells or ([(0, 0)] if valid(0, 0) else [])
    best_t = None
    best_v = None
    for tx, ty in targets[:40]:
        if not valid(tx, ty):
            continue
        d1 = md(sx, sy, tx, ty)
        d2 = md(ox, oy, tx, ty)
        edge_bonus = 0
        if tx in (0, w - 1) or ty in (0, h - 1):
            edge_bonus = -2
        v = d1 + 0.35 * d2 + edge_bonus
        if best_v is None or v < best_v or (v == best_v and (tx, ty) < best_t):
            best_v, best_t = v, (tx, ty)

    tx, ty = best_t if best_t is not None else (sx, sy)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        toward = abs(nx - tx) + abs(ny - ty)
        away = md(ox, oy, nx, ny)
        cand.append((toward - 0.15 * away, -away, dx, dy))
    cand.sort()
    if not cand:
        return [0, 0]
    return [int(cand[0][2]), int(cand[0][3])]