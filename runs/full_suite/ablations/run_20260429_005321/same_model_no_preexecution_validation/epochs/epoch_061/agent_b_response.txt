def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy): return [0, 0]
    if not resources: return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None: return [0, 0]
    if opd is None: opd = [[INF] * w for _ in range(h)]

    best = None; best_score = -10**18
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF: continue
        # Prefer resources we can reach first; also avoid giving opponent advantage.
        score = (do - dm) * 10 - dm
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None: return [0, 0]
    tx, ty = best

    # Move one step to reduce our distance; tie-break by increasing (opponent - mine).
    best_step = [0, 0]; step_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        dm2 = myd[ny][nx]  # exact from BFS
        do2 = opd[ny][nx]
        # Convert next position to expected advantage toward target using distance-to-target BFS.
        # Approximation: use our distance to target from myd arrays.
        dmy_to_t = myd[ty][tx]  # constant but keep structure; ignore
        # Better: evaluate by direct target distances computed from my BFS for each candidate:
        dm_to = myd[ty][tx]  # not useful; instead use greedy to target via coordinate deltas + BFS dist
        # Use target distance from candidate: need BFS from candidate would be expensive.
        # Instead: approximate by moving that most decreases Euclidean to target; deterministic.
        eu = abs(nx - tx) + abs(ny - ty)
        # Opponent advantage if we step away from them: use their distance from same candidate.
        adv = (opd[ny][nx] - myd[ny][nx])
        sc = -eu + adv * 0.01
        if sc > step_score:
            step_score = sc
            best_step = [dx, dy]

    return best_step