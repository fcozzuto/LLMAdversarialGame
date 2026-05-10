def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        sx0, sy0 = start
        if not inb(sx0, sy0):
            return dist
        dist[sx0][sy0] = 0
        qx, qy = [sx0], [sy0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    # Pursuer tries to minimize shortest-path distance to evader; Evader maximizes it.
    pursuer_pos = (sx, sy) if "pursuer" in self_role else (ox, oy)
    other_pos = (ox, oy) if "pursuer" in self_role else (sx, sy)
    dist_from_pursuer = bfs(pursuer_pos)

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist_from_pursuer[nx][ny]
        if d >= 10**9:
            continue
        # Add a small obstacle-near penalty to reduce zigzagging into dead-ends.
        adj_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                adj_obs += 1
        score = d - 0.03 * adj_obs
        # If we're the pursuer, smaller distance is better => invert.
        score = -score if "pursuer" in self_role else score
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]