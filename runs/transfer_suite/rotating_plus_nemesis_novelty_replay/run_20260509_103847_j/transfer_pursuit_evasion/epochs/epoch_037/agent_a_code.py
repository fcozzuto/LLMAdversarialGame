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
                    if (nx, ny) == goal:
                        return d
                    q.append((nx, ny))
        return 10**9

    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy))
        # tie-breakers: prefer safer movement and stay away from edges for evader, toward center for pursuer
        edge = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        # small deterministic penalty for stepping closer to obstacles: encourages not colliding/wrapping
        near_obs = 0
        for ax, ay in obs:
            ddx, ddy = nx - ax, ny - ay
            near_obs += (ddx * ddx + ddy * ddy <= 1)
        if is_evader:
            val = d * 100.0 - edge * 1.5 - near_obs * 2.0
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            val = d * 100.0 + edge * 0.3 + near_obs * 2.0
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]