def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
            return None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Deterministic tie-break: lexicographic on (margin, -own_dist, -opp_dist, nx, ny)
    best = None
    for dx, dy, nx, ny in candidates:
        own_best = None
        for rx, ry in rpos:
            d_self = abs(rx - nx) + abs(ry - ny)
            d_opp = abs(rx - ox) + abs(ry - oy)
            margin = d_opp - d_self
            key = (margin, -d_self, -d_opp, rx, ry)
            if own_best is None or key > own_best:
                own_best = key
        score = own_best[:3] + (nx, ny)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]