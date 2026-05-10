def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    self_is_pursuer = not self_is_evader

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(startx, starty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(startx, starty):
            return dist
        dist[startx][starty] = 0
        qx, qy, qi = [startx], [starty], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    # If pursuer: minimize distance to evader; if evader: maximize distance from pursuer.
    if self_is_pursuer:
        dist_from_opp = bfs(ox, oy)  # pursuer wants dist_from_opp[next] small
        best = None
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist_from_opp[nx][ny]
            if d < best_d or (d == best_d and (best is None or (dx, dy) < best)):
                best_d, best = d, (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Evader
    dist_from_self = bfs(ox, oy)  # distance from pursuer to candidate
    # Also add a slight preference to move toward grid-center to avoid edge traps.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist_from_self[nx][ny]
        if d >= 10**8:
            # unreachable means blocked off; still treat as very good but deterministic tie-breaker
            d = 10**6
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.001
        score = d + center_bias
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score, best = score, (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]