def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        sx0, sy0 = start
        if not inside(sx0, sy0) or not inside(goal[0], goal[1]):
            return 10**9
        dist = [[-1] * h for _ in range(w)]
        q = [(sx0, sy0)]
        dist[sx0][sy0] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            if (x, y) == goal:
                return dist[x][y]
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and dist[nx][ny] == -1:
                    if (nx, ny) == goal:
                        return nd
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return 10**9

    # If no obstacles or target unreachable, fall back to direct direction heuristic.
    d_to_opp = bfs_dist((sx, sy), (ox, oy))
    use_bfs = d_to_opp < 10**8

    if not use_bfs:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        if is_evader:
            dx, dy = -dx, -dy
        return [int(dx), int(dy)]

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        d1 = bfs_dist((nx, ny), (ox, oy))
        # pursuer minimizes distance, evader maximizes distance; tie-break by Manhattan for stability
        if is_evader:
            key = (d1, abs(nx - ox) + abs(ny - oy))
            better = (best_val is None) or (key > best_val)
        else:
            key = (-d1, -(abs(nx - ox) + abs(ny - oy)))
            better = (best_val is None) or (key > best_val)
        if better:
            best_val = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]