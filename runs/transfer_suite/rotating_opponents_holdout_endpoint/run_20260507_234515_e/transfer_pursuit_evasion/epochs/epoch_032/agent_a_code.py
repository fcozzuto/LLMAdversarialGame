def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("direct" in role and "evad" not in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        sx0, sy0 = start
        gx, gy = goal
        if not inside(gx, gy) or (gx, gy) in oset:
            return 10**9
        if not inside(sx0, sy0) or (sx0, sy0) in oset:
            return 10**9
        dist = [[-1] * h for _ in range(w)]
        dist[sx0][sy0] = 0
        qx, qy = [sx0], [sy0]
        qi = 0
        step8 = moves
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in step8:
                nx, ny = x + dx, y + dy
                if not inside(nx, ny) or (nx, ny) in oset:
                    continue
                if dist[nx][ny] == -1:
                    dist[nx][ny] = d
                    if (nx, ny) == (gx, gy):
                        return d
                    qx.append(nx)
                    qy.append(ny)
        return 10**9

    # If capture ends game with radius 0, immediate adjacency matters; BFS handles obstacles.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue

        # Prefer avoiding giving the pursuer/evader an immediate advantage by reducing/increasing BFS distance.
        dpath = bfs_dist((nx, ny), (ox, oy))

        # Tie-break: move also away/toward in Euclidean-ish sense for stability.
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        wall = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)

        if is_pursuer:
            val = (-dpath, -dist2, wall)  # minimize path, then maximize closeness, then slight center
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            val = (dpath, dist2, wall)  # maximize path, then maximize separation, then slight center escape
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]