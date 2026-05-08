def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    if (sx, sy) in set((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2):
        return [0, 0]

    def man(a, b, c, d):  # Manhattan
        return abs(a - c) + abs(b - d)

    # pick target with strongest deterministic "we-are-closer" advantage
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obst:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        nd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # tie-break: prefer moves that increase our relative advantage (even though opponent position is static this turn)
        new_adv = nod - nd
        key = (nd, -new_adv, abs((tx - nx)) + abs((ty - ny)), dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]