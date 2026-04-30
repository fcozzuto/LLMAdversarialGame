def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    resource_cells = set((r[0], r[1]) for r in resources)
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    opp_dist = bfs((ox, oy))
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If only move to immediate resource, keep simple.
    if resource_cells:
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in resource_cells:
                # immediate grab: always best
                return [dx, dy]
    if not resource_cells:
        # No resources known: drift to maximize distance from opponent
        best = None; best_d = -INF
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = max(abs(nx - ox), abs(ny - oy))
            if d > best_d:
                best_d = d; best = (dx, dy)
        return [best[0], best[1]]

    # Race for resources: maximize advantage (opp_steps - our_steps) over all reachable resources.
    best_move = legal[0]
    best_val = -INF
    best_tie = INF  # our_steps for tie-breaking
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_dist = bfs((nx, ny))
        local_best = -INF
        local_best_steps = INF
        for rx, ry in resource_cells:
            od = opp_dist[ry][rx]
            nd = our_dist[ry][rx]
            if nd >= INF or od >= INF:
                continue
            # Positive means we reach earlier; strongly prefer that.
            val =