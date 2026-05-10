def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        sx0, sy0 = start
        gx, gy = goal
        if not inside(sx0, sy0) or not inside(gx, gy):
            return 10**9
        q = [(sx0, sy0)]
        dist = [[-1] * h for _ in range(w)]
        dist[sx0][sy0] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = d
                    if nx == gx and ny == gy:
                        return d
                    q.append((nx, ny))
        return 10**9

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")
    target = (ox, oy)

    best_moves = []
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = bfs_dist((nx, ny), target)
        if is_evader:
            val = d
        else:
            val = -d  # minimize distance to opponent
        if best_val is None or val > best_val:
            best_val = val
            best_moves = [(dx, dy, d)]
        elif val == best_val:
            best_moves.append((dx, dy, d))

    # Tie-break: prefer staying off the same cell if possible, then prefer direction that changes x/y deterministically.
    if not best_moves:
        return [0, 0]
    # Sort by: (changed_pos, distance_to_target, dx, dy) with sign depending on role
    def tie_key(item):
        dx, dy, d = item
        changed = 0 if (dx == 0 and dy == 0) else 1
        if is_evader:
            return (changed, d, dx, dy)
        else:
            return (changed, -d, dx, dy)

    best_moves.sort(key=tie_key, reverse=True)
    return [best_moves[0][0], best_moves[0][1]]