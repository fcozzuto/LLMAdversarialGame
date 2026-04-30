def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Choose target: maximize gap (opponent farther than me), then prefer closer to me.
    best = None; best_key = (-INF, INF)
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        gap = do - dm
        key = (gap, dm)
        if gap > best_key[0] or (gap == best_key[0] and dm < best_key[1]):
            best_key = key; best = (rx, ry)

    # Build candidate moves.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    if best is None:
        # No reachable resources: move to maximize distance from opponent.
        bd = -1; pick = (0, 0)
        for dx, dy, nx, ny in candidates:
            d = max(abs(nx - ox), abs(ny - oy))
            if d > bd:
                bd = d; pick = (dx, dy)
        return [pick[0], pick[1]]

    tx, ty = best
    # Prefer step that reduces my distance to target; slight bias to keep advantage.
    cur_dm = myd[sy][sx]
    best_move = (0, 0); best_score = (-INF, INF)
    for dx, dy, nx, ny in candidates:
        ndm = myd[ny][nx]
        if ndm >= INF:
            continue
        ndo = opd[ny][nx]  # opponent dist from your hypothetical cell (used only for tie bias)
        # Score: primary minimize ndm, secondary maximize (opd[target] - ndm) via best_key[0].
        # Convert to tuple with higher-is-better using keys.
        adv = opd[ty][tx] - ndm
        score = (adv, -ndm)  # maximize adv, then maximize -ndm (= minimize ndm)
        if score[0] > best_score[0] or (score[0] == best_score[0] and score[1] > best_score[1]):
            best_score = score; best_move = (dx, dy)

    # If somehow all equal, deterministic fallback: stay.
    if best_move is None:
        best_move = (0, 0)
    return [best_move[0], best_move[1]]