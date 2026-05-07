def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    p = observation.get("self_position") or [0, 0]
    q = observation.get("opponent_position") or [0, 0]
    sx, sy = int(p[0]), int(p[1])
    ox, oy = int(q[0]), int(q[1])

    blocked = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
        except:
            pass

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = (abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy), nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(x, y):
        md = 10**9
        mt = None
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < md:
                md, mt = d, (rx, ry)
        return md, mt

    opp_md, opp_target = nearest_dist(ox, oy)
    scored = []
    for dx, dy, nx, ny in moves:
        my_md, my_target = nearest_dist(nx, ny)
        # Prefer reducing our distance to a resource.
        # Also slightly prefer moves that keep the opponent farther from their nearest resource.
        # Deterministic tie-break: lexicographic on (score, dx, dy, nx, ny).
        new_opp_md, new_opp_target = nearest_dist(ox, oy)
        delta_opp = new_opp_md - opp_md  # usually 0, but deterministic
        score = (-my_md, delta_opp, nx, ny)
        scored.append((score, dx, dy))
    scored.sort(key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3], t[1], t[2]))
    _, dx, dy = scored[0]
    return [int(dx), int(dy)]