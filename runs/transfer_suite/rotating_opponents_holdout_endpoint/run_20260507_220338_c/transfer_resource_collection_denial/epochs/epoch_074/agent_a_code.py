def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (int(p[0]), int(p[1]))
            if q not in obst:
                res.append(q)
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        ax = int(ax); ay = int(ay); bx = int(bx); by = int(by)
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_sc = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        sc = (od - sd, -sd, rx, ry)
        if best is None or sc > best_sc:
            best = (rx, ry)
            best_sc = sc
    tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            self_race = opp_d - d
            candidates.append((self_race, -d, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]