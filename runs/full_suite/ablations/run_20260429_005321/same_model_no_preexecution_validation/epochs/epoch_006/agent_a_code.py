def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]; qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in set((r[0], r[1]) for r in resources):
                return [dx, dy]
    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))
    best = None; bestv = -10**18
    res_set = set((r[0], r[1]) for r in resources)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dself = our_dist[ny][nx]
        if dself >= 10**8:
            continue
        # choose target that we can reach earlier than opponent
        v = 0
        for rx, ry in res_set:
            ds = our_dist[ry][rx]
            do = opp_dist[ry][rx]
            if ds >= 10**8:
                continue
            if do >= 10**8:
                v += 3.0 * (-ds) + 0.2  # free resource: strongly prefer
            else:
                # positive when we are earlier; also prefer closer to target
                v += (do - ds) - 0.1 * ds
        # mild pressure to avoid being trapped near opponent
        opp_d_here = max(0, our_dist[ny][nx] - 0)  # keep deterministic, bounded influence
        v += -0.05 * (abs(nx - ox) + abs(ny - oy))
        v += 0.001 * (-opp_d_here)
        if v > bestv:
            bestv = v; best = (dx, dy)
    if best is None:
        best = min(legal, key=lambda m: (abs((sx+m[0])-ox)+abs((sy+m[1])-oy), m[0], m[1]))
    return [int(best[0]), int(best[1])]