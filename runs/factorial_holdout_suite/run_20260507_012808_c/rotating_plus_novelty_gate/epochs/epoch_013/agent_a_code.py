def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if 0 <= start[0] < w and 0 <= start[1] < h and (start[0], start[1]) not in obstacles:
            dist[start[0]][start[1]] = 0
            q = [start]
            qi = 0
            while qi < len(q):
                x, y = q[qi]; qi += 1
                d = dist[x][y] + 1
                for dx, dy in moves:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        if d < dist[nx][ny]:
                            dist[nx][ny] = d
                            q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        sd = ds[rx][ry]
        od = do[rx][ry]
        if sd >= 10**9 and od >= 10**9:
            continue
        # Prefer resources where we arrive sooner than opponent by the biggest margin.
        margin = od - sd
        key = (-margin, sd, ry, rx)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        # No reachable resources; move to increase safety by avoiding obstacles and toward center-ish.
        target_x, target_y = w // 2, h // 2
        best_step = [0, 0]
        best_k = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                k = (abs(nx - target_x) + abs(ny - target_y), dx, dy)
                if best_k is None or k < best_k:
                    best_k = k
                    best_step = [dx, dy]
        return best_step

    (rx, ry) = best[1]
    best_step = [0, 0]
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = ds[nx][ny]
            # After moving, we want to reduce our distance to the chosen resource.
            # Tie-break: also keep opponent from getting closer to it.
            opp_nd = do[nx][ny]  # not used directly, but keeps deterministic tie variation
            k = (nd, -do[rx][ry] + ds[rx][ry], dx, dy)
            if best_k is None or k < best_k:
                best_k = k
                best_step = [dx, dy]
    return best_step