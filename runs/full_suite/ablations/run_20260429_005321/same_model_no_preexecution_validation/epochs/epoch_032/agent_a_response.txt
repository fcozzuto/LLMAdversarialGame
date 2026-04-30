def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def step_blocked(x, y): return not inb(x, y) or (x, y) in obstacles

    # Evaluate each resource by "tempo advantage": (opp dist - my dist) with fast local BFS depths.
    # Deterministic small BFS: compute shortest distances within depth limit.
    LIMIT = 6
    INF = 10**9
    def local_dists(start):
        x0, y0 = start
        if step_blocked(x0, y0):
            return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[y][x]
            if d >= LIMIT: 
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = local_dists((sx, sy))
    opd = local_dists((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Choose target with best advantage; tie-break by closer to me, then by coordinate.
    bestT = None
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        adv = do - dm
        key = (adv, -dm, -do, rx, ry)  # maximize adv, then minimize dm, then minimize do
        if bestT is None or key > bestT[0]:
            bestT = (key, (rx, ry))
    if bestT is None:
        # Fallback: go toward resource with minimal my local distance (still obstacle-aware one step).
        candidates = []
        for rx, ry in resources:
            dm = myd[ry][rx]
            if dm < INF:
                candidates.append((dm, rx, ry))
        if not candidates:
            return [0, 0]
        candidates.sort()
        tx, ty = candidates[0][1], candidates[0][2]
    else:
        tx, ty = bestT[1]

    # One-step selection: among legal moves, pick that maximizes (oppDist - myDist) after move, else move closer to target.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if step_blocked(nx, ny):
            continue
        my_next = local_dists((nx, ny))
        if my_next is None:
            continue
        dm = my_next[ty][tx]
        do = opd[ty][tx]
        if dm >= INF:
            score1 = -INF
        else:
            score1 = do - dm
        # primary: tempo advantage to target; secondary: reduce distance to target; tertiary: keep away from opponent if equal
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(ox - nx) + abs(oy - ny)
        key = (score1, -dist_to_target, opp_dist, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    if best is not None:
        return best[1]

    # Last resort deterministic: go greedily toward target by sign, with diagonal preference order from dirs.
    gx = 0 if tx == sx else (1 if tx > sx else -1)
    gy = 0 if ty == sy else (1 if ty > sy else -1)
    for dx, dy in dirs:
        if dx == gx or (dx == 0 and gx == 0):
            if dy == gy or (dy == 0 and gy