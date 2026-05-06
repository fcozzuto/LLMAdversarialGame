def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep(p):
        if isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    rpos = []
    for r in resources:
        q = rep(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    if not rpos:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        best_val = -10**9
        best_selfd = 10**9
        best_oppd = 10**9
        for rx, ry in rpos:
            self_d = md((nx, ny), (rx, ry))
            opp_d = md((ox, oy), (rx, ry))
            val = opp_d - self_d
            if val > best_val or (val == best_val and (self_d < best_selfd or (self_d == best_selfd and opp_d < best_oppd))):
                best_val = val
                best_selfd = self_d
                best_oppd = opp_d
        # Prefer moves that (1) win races, (2) reduce distance to that winning target,
        # (3) also reduce opponent distance as a fallback when losing.
        key = (best_val, -best_selfd, -best_oppd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]