def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            d = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best_score = -10**18
    best_t = None
    # Target resources we can reach sooner than opponent; otherwise still pick one with best relative gap.
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        dm = myd[ry][rx]
        do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        # Prefer: maximize (do - dm), then prefer closer to me, then avoid giving opponent huge advantage.
        rel = (do - dm) if (dm < INF and do < INF) else (10**6 if do >= INF else -10**6)
        score = rel * 1000 - dm
        if score > best_score:
            best_score = score
            best_t = (rx, ry)
        elif score == best_score and best_t is not None:
            # deterministic tie-break by coordinates
            if (rx, ry) < best_t:
                best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Evaluate moves by resulting distance to target and effect on opponent's distance to the same target.
    cur_dm = myd[sy][sx]
    cur_do = opd[ty][tx]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dm2 = myd[ny][tx]
        do2 = opd[ny][tx]  # opponent distance proxy isn't directly for them; use target distance from where opponent could be in future? Instead use our move only.
        # Use current opponent distance to target (fixed) but encourage not losing relative tempo by reducing dm2.
        val = (-dm2) * 10 + (cur_do - dm2)
        # small bias to avoid drifting away if no improvement
        if dm2 > cur_dm:
            val -= 2
        if val > best_val or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return best_move