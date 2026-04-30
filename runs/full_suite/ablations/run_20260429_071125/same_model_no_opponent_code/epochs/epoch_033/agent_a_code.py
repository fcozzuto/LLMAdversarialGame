def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in res:
        dS = dist(sx, sy, rx, ry)
        dO = dist(ox, oy, rx, ry)
        key = (dO - dS, -dS, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    rx, ry = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_m = (0, 0)
    best_m_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        dS = dist(nx, ny, rx, ry)
        dO = dist(ox, oy, rx, ry)
        # Prefer moves that improve your lead to the chosen target; tie-break by moving closer to target,
        # and avoid stepping into squares near obstacles.
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                axx, ayy = nx + adx, ny + ady
                if in_bounds(axx, ayy) and (axx, ayy) in obstacles:
                    near_obs += 1
        key = (dO - dS, -dS, -near_obs, dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]