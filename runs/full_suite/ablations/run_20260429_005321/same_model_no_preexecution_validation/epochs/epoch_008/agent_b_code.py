def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
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
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    # Choose a target resource and a move that helps us reach it sooner while keeping opponent farther.
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_best = INF
        opp_best = INF
        for r in resources:
            rx, ry = r[0], r[1]
            d1 = our_dist[ry][rx]
            d2 = opp_dist[ry][rx]
            # estimate our distance from next cell via simple adjustment if within grid
            # (BFS metric is uniform step, use next-cell distance to resource from next cell by computing local step)
            # Instead of full recompute, approximate by (d from current) - 1 if next closer in BFS.
            # This stays deterministic and effective in practice.
            # Determine if next step moves along a shortest path to resource.
            our_next = our_dist[ny][rx]
            opp_next = opp_dist[ry][rx]
            if our_next < our_best:
                our_best = our_next
            if opp_next < opp_best:
                opp_best = opp_next
        val = -our_best + 0.35 * opp_best + 0.01 * (nx + ny)  # tie-break deterministically
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]