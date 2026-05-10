def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    obstacles = observation.get("obstacles") or []
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_dist(a, b):
        if a == b:
            return 0
        ax, ay = a
        if not inb(ax, ay) or not inb(b[0], b[1]):
            return 10**9
        q = [(ax, ay)]
        seen = {(ax, ay)}
        d = 0
        while q:
            nq = []
            for x, y in q:
                for dx, dy in moves:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in seen or not inb(nx, ny):
                        continue
                    if nx == b[0] and ny == b[1]:
                        return d + 1
                    seen.add((nx, ny))
                    nq.append((nx, ny))
            q = nq
            d += 1
        return 10**9

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    # Deterministic tie-breaking preference
    # (Wall-runner tends to exploit staying aligned; we prefer axis/diagonal that changes direction.)
    move_order = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cand = []
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine keeps you in place on invalid move
        dist = bfs_dist((nx, ny), (ox, oy))
        # Obstacle "pressure": prefer staying with fewer adjacent obstacles (evade) or more (pursue)
        adj = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs_set:
                adj += 1
        # Also gently prefer moving away/toward opponent in Manhattan if BFS ties (handles unreachable areas).
        manh = abs(nx - ox) + abs(ny - oy)
        if pursuer:
            score = (-dist, manh, adj)  # maximize tuple: want smaller dist -> larger negative
        else:
            score = (dist, -manh, -adj)  # want larger dist, smaller manh doesn't matter, less obstacle adj helps
        cand.append((score, [dx, dy]))

    cand.sort(key=lambda t: t[0], reverse=True)
    return cand[0][1]