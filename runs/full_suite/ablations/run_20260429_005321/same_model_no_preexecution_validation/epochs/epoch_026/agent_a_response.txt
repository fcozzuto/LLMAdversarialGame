def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obs:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None  # (adv, -my_dist, my_dist, rx, ry)
    for rx, ry in resources:
        dm, do = myd[ry][rx], opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        adv = do - dm
        cand = (adv, -dm, dm, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, dm_best, tx, ty = best
    if dm_best >= INF:
        tx, ty = resources[0]  # deterministic fallback

    # Move to neighbor that minimizes our distance to target (tie-breaker: closer to avoid opponent)
    best_step = (INF, INF, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_dist = myd[ny][nx]
        op_dist = opd[ny][nx]
        cand = (my_dist, -op_dist, dx, dy)
        if my_dist < best_step[0] or (my_dist == best_step[0] and cand[1] > best_step[1]):
            best_step = cand

    return [best_step[2], best_step[3]]