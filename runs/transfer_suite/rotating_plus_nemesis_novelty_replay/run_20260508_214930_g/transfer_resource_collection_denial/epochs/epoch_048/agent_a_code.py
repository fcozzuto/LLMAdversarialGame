def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource where we are (relatively) closer than opponent.
    best_t = None
    best_key = None
    for t in res:
        self_d = cheb((sx, sy), t)
        opp_d = cheb((ox, oy), t)
        # Prefer targets where we can beat opponent (smaller margin), then nearer overall.
        key = (self_d - opp_d, self_d)
        if best_key is None or key < best_key:
            best_key = key
            best_t = t

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # One-step lookahead: improve our advantage vs opponent for the same target,
        # while also making it harder for opponent to catch up (minimize their next distance).
        self_d2 = cheb((nx, ny), (tx, ty))
        opp_d2 = cheb((ox, oy), (tx, ty))
        # Approximate opponent next distance by assuming they move to reduce Chebyshev distance.
        odx = (tx - ox)
        if odx != 0: odx = 1 if odx > 0 else -1
        ody = (ty - oy)
        if ody != 0: ody = 1 if ody > 0 else -1
        nax, nay = ox + odx, oy + ody
        if not inb(nax, nay) or (nax, nay) in obs:
            nax, nay = ox, oy
        opp_d2_next = cheb((nax, nay), (tx, ty))

        # Slightly prefer collecting immediately.
        collect_bonus = 0
        if (nx, ny) == (tx, ty):
            collect_bonus = -1000

        score = (self_d2 - opp_d2_next, self_d2, collect_bonus)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]