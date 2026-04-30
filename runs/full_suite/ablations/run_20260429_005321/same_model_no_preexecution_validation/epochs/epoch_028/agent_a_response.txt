def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if not resources or myd is None or opd is None:
        return [0, 0]

    best = None  # (adv, -my_dist, my_dist, rx, ry)
    for rx, ry in resources:
        dm, do = myd[ry][rx], opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        adv = do - dm
        cand = (adv, -dm if dm < INF else -INF, dm, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    _, _, _, tx, ty = best

    best_move = (INF, -INF, 0, 0)  # (my_to, -op_to, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to = myd[ny][nx] + myd[ty][tx]  # not used as metric; fallback below
        if myd[ny][nx] >= INF or myd[ty][tx] >= INF:
            continue
        # True metric: distance from candidate to target using precomputed dist from candidate is not available.
        # Approximate by one-step improvement: choose move that reduces my distance to target along myd field gradient.
        # Estimate my distance to target from candidate by BFS-from-target would be expensive; instead use myd-to-target from current:
        # We'll use local heuristic: squared distance to target.
        hcur = (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty)
        hn = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if hn > hcur:
            pass
        # Also consider opponent pressure: prefer moves that increase opponent distance to target.
        op_to = opd[ty][tx] - opd[ny][nx] if opd[ny][nx] < INF else -INF
        key = (hn, -op_to, dx, dy)
        if best_move == (INF, -INF, 0, 0) or key < best_move:
            best_move = key

    dx, dy = best_move[2], best_move[3]
    return [dx, dy]