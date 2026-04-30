def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
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

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # fallback: move toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dcen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            doom = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            v = (dcen, -doom, dx, dy)
            if bestv is None or v < bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    # Choose contested target: prefer resources where we are earlier; if we're late, pick one that is still reachable
    best_res = None; best_score = -10**18
    for rx, ry in resources:
        d1 = our_dist[ry][rx]; d2 = opp_dist[ry][rx]
        if d1 >= 10**9 and d2 >= 10**9:
            continue
        # score: gain if we can beat opponent; if not, contest nearest available to reduce their lead
        score = 0
        if d1 < 10**9:
            score += (d2 - d1) * 10
            score += (-(d1))  # nearer is better
        else:
            score -= d2 * 5  # only contest if we can reach; otherwise avoid
        # encourage grabbing resources closer to opponent's reach only when we can still influence
        score += (10 - min(d2, 10)) if d1 < 10**9 else -999
        # small determinism tie-breaker by coordinates
        score += -0.001 * (rx + 17 * ry)
        if score > best_score:
            best_score = score; best_res = (rx, ry)

    tx, ty = best_res if best_res is not None else resources[0]

    # Select move: minimize our distance to target; break ties by maximizing opponent distance to target and distance from opponent
    best = None; best_t = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d1 = our_dist[ny][nx]
        my_to_t = our_dist[ty][tx]