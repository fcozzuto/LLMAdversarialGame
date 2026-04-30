def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set(map(tuple, observation["obstacles"]))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose best target resource by advantage over opponent
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((x, y), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we are closer to; break ties deterministically
            key = (ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: move toward opponent to contest/deny
        tx, ty = ox, oy

    deltas = [(0,0), (1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]
    cur = (x, y)

    # Evaluate candidate moves
    ranked = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        # Prefer steps that reduce distance to target; lightly prefer not moving away
        nd = dist((nx, ny), (tx, ty))
        cd = dist(cur, (tx, ty))
        prefer = (nd, -int(nd < cd), abs(dx) + abs(dy), dx, dy)
        ranked.append((prefer, [dx, dy]))

    ranked.sort(key=lambda t: t[0])
    if ranked:
        return ranked[0][1]
    return [0, 0]