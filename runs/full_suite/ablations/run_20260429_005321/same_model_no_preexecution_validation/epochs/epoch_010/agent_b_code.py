def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    def next_pos(dx, dy):
        return sx + dx, sy + dy

    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    # Always compute opponent distance once; ours depends on move.
    opp_dist = bfs((ox, oy))

    if resources:
        res = [(r[0], r[1]) for r in resources]
        best_move = None
        best_val = -INF
        for dx, dy in legal_moves:
            nx, ny = next_pos(dx, dy)
            our_dist = bfs((nx, ny))
            # Evaluate: maximize advantage (opp sooner) over best-contested resource.
            val = -INF
            for rx, ry in res:
                od = opp_dist[ry][rx]
                od = od if od < INF else 10**6
                nd = our_dist[ry][rx]
                nd = nd if nd < INF else 10**6
                # Primary: reach faster; secondary: absolute closeness; tertiary: avoid dead resource unreachable.
                cand = (od - nd) * 10 - nd
                val = cand if cand > val else val
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to center while staying away from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in legal_moves:
        nx, ny = next_pos(dx, dy)
        # maximize center progress and distance from opponent
        dc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        da = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = dc + 0.05 * da
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]