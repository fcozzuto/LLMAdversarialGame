def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start, limit=63):
        if not inb(start[0], start[1]) or start in obstacles:
            return None
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[y][x]
            if d >= limit: 
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF and od >= INF:
            continue
        # Favor resources where we are closer; small tie-break by resource position
        adv = (od - md)
        # If we can reach, prioritize reaching; if opponent can't, strongly prioritize.
        reachable = 1 if md < INF else 0
        opp_reachable = 1 if od < INF else 0
        score = (reachable * 1000) - (opp_reachable * 500) + adv
        key = (score, -(md if md < INF else INF), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Choose move that minimizes our distance to target; deterministic tie-break by move.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = myd[ny][nx]
        candidates.append((d, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]