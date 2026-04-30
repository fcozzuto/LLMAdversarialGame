def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            x = p.get("x", None)
            y = p.get("y", None)
            if x is not None and y is not None:
                return int(x), int(y)
            pos = p.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return int(pos[0]), int(pos[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        q = to_xy(p)
        if q is not None:
            obstacles.add(q)

    resources = []
    for p in observation.get("resources", []) or []:
        q = to_xy(p)
        if q is not None:
            resources.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if d < dmin:
                    dmin = d
            # Prefer collecting/approaching nearest resource, keep distance from opponent slightly.
            val = -dmin * 3 + dist_opp * 0.3
        else:
            # No resources visible: just drift away from opponent and avoid obstacles.
            val = dist_opp
        cand.append((val, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]