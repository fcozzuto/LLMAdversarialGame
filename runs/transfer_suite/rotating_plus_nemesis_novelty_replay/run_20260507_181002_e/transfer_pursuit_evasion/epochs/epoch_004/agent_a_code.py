def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    start = (ox, oy)
    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    q = [start]; dist[start[0]][start[1]] = 0; qi = 0
    while qi < len(q):
        x, y = q[qi]; qi += 1
        nd = dist[x][y] + 1
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_bonus(x, y):
        b = 0
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if d > b: b = d
        return b

    best = None
    best_val = -INF if not is_pursuer else INF
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            d = dist[nx][ny]
            if d >= INF: 
                continue
            # Pursuer: minimize distance to opponent; Evader: maximize.
            val = d * (1 if is_pursuer else -1) + (0 if is_pursuer else -corner_bonus(nx, ny) * 0.01) + (0 if not is_pursuer else corner_bonus(nx, ny) * 0.01)
            if best is None or (is_pursuer and val < best_val) or ((not is_pursuer) and val > best_val):
                best_val = val
                best = (dx, dy)

    return list(best) if best is not None else [0, 0]