def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    dirs.append((0, 0))

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    qx = [ox]; qy = [oy]; dist[ox][oy] = 0; qi = 0
    while qi < len(qx):
        x = qx[qi]; y = qy[qi]; qi += 1
        nd = dist[x][y] + 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny) and nd < dist[nx][ny]:
                dist[nx][ny] = nd
                qx.append(nx); qy.append(ny)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = corners[observation.get("turn_index", 0) % 4]

    best = None
    best_val = -INF if not is_pursuer else INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        d = dist[nx][ny]
        md = abs(nx - ox) + abs(ny - oy)
        cornerish = abs(nx - corner[0]) + abs(ny - corner[1])
        away = (nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)  # prefer pushing further from pursuer when evading
        if is_pursuer:
            # minimize distance to opponent; prefer blocking with cornerish as secondary
            val = d * 1000 - cornerish - away * 1e-3
            if val < best_val:
                best_val = val; best = (dx, dy)
        else:
            # maximize distance to opponent; tie-break by increasing manhattan and going toward a rotating corner
            val = d * 1000 + md * 10 + cornerish
            if val > best_val:
                best_val = val; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]