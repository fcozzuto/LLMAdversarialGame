def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = observation.get("obstacles", [])
    obstacles = set()
    for p in obs:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    resources = observation.get("resources", [])
    res = []
    for r in resources:
        try:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                res.append((x, y))
        except:
            pass

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(0, 0)]
    for d in (1,):
        pass
    pref = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    seen = set()
    ordered = []
    for m in pref:
        if m not in seen:
            ordered.append(m); seen.add(m)
    best = None
    best_key = None

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if res:
            mind = None
            for rx, ry in res:
                d = dist((nx, ny), (rx, ry))
                if mind is None or d < mind:
                    mind = d
            # Also mildly prefer moving away from opponent to reduce contest.
            oppd = dist((nx, ny), (ox, oy))
            key = (mind, -oppd, dx, dy)
        else:
            # No resources: move toward opponent.
            key = (dist((nx, ny), (ox, oy)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best