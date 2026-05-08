def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start, limit=12):
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[(x, y)]
            if d >= limit: continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) not in dist:
                        dist[(nx, ny)] = d + 1
                        q.append((nx, ny))
        return dist

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    opd = bfs((ox, oy), 12)
    INF = 10**9
    best_move, best_val = (0, 0), -INF
    dirs = legal[:]  # deterministic order already: dx then dy
    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        sd = bfs((nx, ny), 12)
        val = -INF
        for rx, ry in res:
            d_self = sd.get((rx, ry), INF)
            d_op = opd.get((rx, ry), INF)
            if d_self >= INF or d_op >= INF: 
                continue
            margin = d_op - d_self
            # If we can reach earlier (positive margin), strongly prefer; also prefer closer overall.
            score = margin * 30 - d_self
            if score > val: val = score
        # If all resources unreachable, fall back to best step toward nearest resource not blocked.
        if val == -INF:
            nd = INF
            for rx, ry in res:
                d = abs(nx - rx) + abs(ny - ry)
                if d < nd: nd = d
            val = -nd
        if val > best_val:
            best_val, best_move = val, (dx0, dy0)
    return [best_move[0], best_move[1]]