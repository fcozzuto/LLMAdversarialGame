def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inf = 10**9

    role = observation.get("self_role", "pursuer")
    if role not in ("pursuer", "evader"):
        role = "pursuer"
    target = (ox, oy)
    dist = [[inf] * h for _ in range(w)]
    if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obs:
        q = [(ox, oy)]
        qi = 0
        dist[ox][oy] = 0
        while qi < len(q):
            cx, cy = q[qi]
            qi += 1
            nd = dist[cx][cy] + 1
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[nx][ny]
        if d >= inf:
            d = 10**6
        manh = abs(nx - ox) + abs(ny - oy)
        if role == "pursuer":
            key = (d, manh, dx, dy)  # minimize distance to opponent
        else:
            key = (-d, -manh, dx, dy)  # maximize distance from opponent
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]