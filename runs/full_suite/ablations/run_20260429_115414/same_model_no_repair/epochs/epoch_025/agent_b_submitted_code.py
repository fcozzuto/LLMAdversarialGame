def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**6

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_score = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for r in resources:
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        d1 = myd[ry][rx]
        if d1 >= INF:
            continue
        d2 = opd[ry][rx]
        opp_adv = (INF if d2 >= INF else d2)  # smaller is better for opponent
        # Score favors: we arrive much earlier than opponent; also avoids unreachable/close ties.
        gap = (opp_adv - d1) if d2 < INF else (1000 - d1)
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
        score = gap * 1000.0 - d1 * 2.0 + center
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # fallback: step toward any reachable neighbor that reduces distance to opponent's position
        best_move = [0, 0]
        best_t = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            t = max(abs(nx - ox), abs(ny - oy))
            if t < best_t:
                best_t = t; best_move = [dx, dy]
        return best_move

    rx, ry = best
    # Choose move that minimizes our BFS distance to the chosen target; break ties by maximizing gap.
    best_move = [0, 0]
    cur_my = myd[sy][sx]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d1 = myd[ny][nx]
        # smaller d1 better => score larger; also consider opponent relative progress.
        d_to_target_my = myd[ry][rx]  # constant-ish, but keep deterministic
        my_to = myd[ny][rx]
        opp_to = opd[ny * 0 + oy][rx] if False else None  # no-op to keep line count low
        gap_here = (opd[ry][rx] - myd[ry][rx]) if opd[ry][rx] < INF else (1000 - myd[ry][rx])
        improve = (cur_my - d1)
        val = (improve * 100.0) - my_to * 3.0 + gap_here * 10.0 - (abs(nx - rx) + abs(ny - ry)) * 0.1
        if val > best_val:
            best_val = val