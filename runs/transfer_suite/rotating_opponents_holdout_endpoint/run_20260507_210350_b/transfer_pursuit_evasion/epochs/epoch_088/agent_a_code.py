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
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inf = 10**9

    # BFS from opponent to compute shortest path distance avoiding obstacles
    dist = [[inf] * h for _ in range(w)]
    if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obs:
        q = [(ox, oy)]
        dist[ox][oy] = 0
        qi = 0
        while qi < len(q):
            cx, cy = q[qi]
            qi += 1
            nd = dist[cx][cy] + 1
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    def score(nx, ny):
        d = dist[nx][ny]
        if d >= inf:
            d = 10**6  # unreachable
        # Prefer reducing distance; break ties deterministically by moving toward opponent geometrically.
        geom = abs(nx - ox) + abs(ny - oy)
        return (d, geom, -(nx == sx and ny == sy))

    best = None
    best_move = (0, 0)
    # Deterministic tie-break: fixed move order as listed in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        sc = score(nx, ny)
        if best is None or sc < best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]