def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy): return [0, 0]
    if any((sx, sy) == (rx, ry) for rx, ry in resources): return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        q = [(start[0], start[1])]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    if myd is None or not resources: return [0, 0]
    opd = bfs((ox, oy)) or [[INF]*w for _ in range(h)]

    beta = 0.95
    best = None
    best_val = -10**18
    prefer_margin = 2  # small push to pick resources we can beat
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF: continue
        # Higher is better: prioritize low own distance, and being earlier than opponent
        val = -(d1) + beta*(d2 - d1)
        if d2 - d1 >= prefer_margin: val += 3
        # Deterministic tie-break using turn_index
        val += 0.00001*((observation["turn_index"] + rx*7 + ry*13) % 100)
        if val > best_val:
            best_val = val; best = (rx, ry)

    tx, ty = best if best is not None else resources[0]
    # Choose best next step by maximizing same objective one move closer
    best_move = [0, 0]
    cur_best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        d1 = myd[ny][nx] + myd[ty][tx] - myd[sy][sx]  # monotone-ish proxy; avoids extra BFS
        # Better: directly use distances to target from start-neighbor
        d1 = myd[ny][tx]  # actual dist from neighbor to target
        d2 = opd[ny][tx]  # proxy for opponent contest (still deterministic)
        if d1 >= INF: continue
        val = -(d1) + beta*(d2 - d1)
        if opd[ty][tx] - d1 >= prefer_margin: val += 3
        val += 0.00001*((observation["turn_index"] + nx*5 + ny*11) % 100)
        if val > cur_best:
            cur_best = val; best_move = [dx, dy]

    # Ensure returned move in {-1,0,1}
    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1: return [0, 0]
    return [int(dx), int(dy)]