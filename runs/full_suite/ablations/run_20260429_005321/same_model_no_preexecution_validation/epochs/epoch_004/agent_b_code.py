def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
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
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    if not resources:
        for dx, dy in sorted(dirs):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0); best_score = -10**18
    for dx, dy in sorted(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d1 = our_dist[ny][nx]  # 0 always if nx,ny are our position; after invalid stays, ok
        # Evaluate by best resource for this move: maximize opponent-lag advantage.
        move_best = -10**18
        for rx, ry in resources:
            du = our_dist[ry][rx]
            do = opp_dist[ry][rx]
            if du >= 10**9:  # unreachable
                continue
            adv = do - du
            # Slight preference for getting closer ourselves; small tie-break on coordinates via score constants.
            val = adv * 100 - du - (rx + ry) * 1e-3
            if val > move_best:
                move_best = val
        # Penalize moves that don't improve: if move_best equals baseline, keep deterministic.
        score = move_best - d1 * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]