def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = []
    for key in ("resources", "unclaimed_cells"):
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    candidates.append((x, y))

    if not candidates:
        candidates = [(ox, oy), (w // 2, h // 2), (0, 0), (w - 1, h - 1)]

    best = None
    best_score = None
    for x, y in candidates:
        ds = manh(sx, sy, x, y)
        do = manh(ox, oy, x, y)
        score = (do - ds, -ds, -x, -y)
        if best_score is None or score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_m = None
    best_m_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = manh(nx, ny, tx, ty)
        do = manh(nx, ny, ox, oy)
        m_score = (do - ds, -ds, -nx, -ny)
        if best_m_score is None or m_score > best_m_score:
            best_m_score = m_score
            best_m = (dx, dy)

    if best_m is None:
        best_m = (0, 0)
    return [int(best_m[0]), int(best_m[1])]