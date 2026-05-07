def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    best = None
    best_key = None
    for x, y in valid_res:
        sd = manh(sx, sy, x, y)
        od = manh(ox, oy, x, y)
        key = (sd, od, x, y)  # first minimize our distance; then opponent distance; then stable tie
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = manh(sx, sy, tx, ty)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = manh(nx, ny, tx, ty)
        oppd = manh(nx, ny, ox, oy)
        cand.append((nd, -oppd, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    chosen = cand[0]
    return [chosen[2], chosen[3]]