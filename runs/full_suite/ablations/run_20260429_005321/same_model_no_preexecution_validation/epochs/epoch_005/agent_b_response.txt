def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))
    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    if not resources:
        # deterministic fallback: move toward center while avoiding obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = -(abs(nx - cx) + abs(ny - cy)) - 0.001 * (dx + 2 * dy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # choose target resource that maximizes our "first arrival advantage"
    best_target = None; best_adv = -10**18
    for rx, ry in resources:
        ds = our_dist[ry][rx]; do = opp_dist[ry][rx]
        if ds >= INF or do >= INF:
            continue
        adv = do - ds  # positive means we are closer
        # prefer being closer even if both are close, deterministically by coord
        score = adv * 1000 - ds
        if score > best_adv or (score == best_adv and (rx, ry) < best_target):
            best_adv = score; best_target = (rx, ry)

    if best_target is None:
        # no reachable resources: just avoid getting stuck against obstacles
        best = (0, 0); bestd = INF
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - ox) + abs(ny - oy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d; best = (dx, dy)
        return [best[0], best[1]]

    rx, ry = best_target

    # among moves, pick the one that reduces our distance to the target most,
    # and if tied, increases the advantage vs opponent.
    best_move = None; best_key = None
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        ds2 = our_dist[ny][rx]
        do2 = opp_dist[ry][ox]  # unused but keeps structure; deterministic key below
        # compute opponent advantage from current state to target directly
        ds0 = our_dist[sy][sx]  # unused, deterministic