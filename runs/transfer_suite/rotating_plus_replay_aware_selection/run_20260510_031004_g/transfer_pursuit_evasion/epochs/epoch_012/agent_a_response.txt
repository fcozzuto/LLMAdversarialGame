def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if not is_pursuer and (("pursuer" in opponent_role) or ("pursuit" in opponent_role) or ("hunter" in opponent_role)):
        is_pursuer = False
    if "evader" in self_role:
        is_pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # BFS distances from opponent to all reachable cells (8-connectivity, avoiding obstacles)
    INF = 10**9
    dist = [[INF for _ in range(h)] for _ in range(w)]
    if valid(ox, oy):
        q = [(ox, oy)]
        qi = 0
        dist[ox][oy] = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    def open_neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    # Choose move: pursuer minimize distance; evader maximize distance; break ties by mobility.
    best_dxdy = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist[nx][ny] if valid(nx, ny) else INF
        mobility = open_neighbors_count(nx, ny)
        # Avoid getting trapped: prefer higher mobility when evading; lower mobility when pursuing (to corner).
        if is_pursuer:
            score = (-d, mobility)
            if best_score is None or score > best_score:
                best_score = score
                best_dxdy = (dx, dy)
        else:
            score = (d, mobility)
            if best_score is None or score > best_score:
                best_score = score
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]