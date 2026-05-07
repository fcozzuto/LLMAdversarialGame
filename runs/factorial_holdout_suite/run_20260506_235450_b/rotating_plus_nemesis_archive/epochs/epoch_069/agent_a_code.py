def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue

        if res:
            closest = 10**9
            for rx, ry in res:
                d = dist((nx, ny), (rx, ry))
                if d < closest:
                    closest = d
            opp = dist((nx, ny), (ox, oy))
            score = -closest * 10 - 2 * dist((nx, ny), (sx, sy)) + opp
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            cen = -((nx - cx) ** 2 + (ny - cy) ** 2)
            opp = dist((nx, ny), (ox, oy))
            score = 2 * opp + cen

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move