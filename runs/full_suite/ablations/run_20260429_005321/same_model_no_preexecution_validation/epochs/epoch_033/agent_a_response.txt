def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    LIMIT = 8
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

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best_key = None
    best_target = None
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        # Prefer reachable resources; then maximize tempo advantage and proximity.
        # Tie-break deterministically by coordinates.
        reachable_me = dm < INF
        reachable_opp = do < INF
        if not reachable_me and reachable_opp:
            # Block: only if we can't reach, still try to deny by maximizing opponent distance.
            key = (0, do, rx, ry)
        else:
            # Main race: higher (do-dm) means we arrive earlier.
            # Also slightly prefer smaller dm to secure faster gains.
            adv = (do - dm) if reachable_opp else (LIMIT + 1)
            key = (1, -adv, dm, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Choose one step that improves my distance to target and (when possible) increases opponent distance margin.
    best_move = (0, 0)
    best_eval = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dm_now = myd[ny][nx]
        # If target is unreachable from here, discourage.
        if dm_now >= INF:
            continue
        # Evaluate with both distances to target.
        my_to_tx = myd[ty][tx]  # constant but keeps structure simple
        # Direct improvement toward target:
        curr_dist_to_target = myd[ty][tx]  # myd already has target dist from current start, not from nx.
        # Instead approximate by Manhattan-ish to target using BFS-local distances is complex; use greedy by delta.
        greedy = -(abs(tx - nx) + abs(ty - ny))
        # Opponent pressure: compare my next-step distance to target with opponent distance from its current position.
        do_tx = opd[ty][tx]
        adv_score = (do_tx - dm_now) if do_tx < INF else (LIMIT + 1)
        eval_score = (adv_score, greedy, -dm_now, nx, ny)
        if best_eval is None or eval_score > best_eval:
            best_eval = eval_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]