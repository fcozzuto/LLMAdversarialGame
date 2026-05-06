def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # Race value: positive means we are closer to the resource than opponent.
    best_r = None
    best_gap = -10**9
    closest_to_opp = resources[0]
    opp_min_d = 10**9
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        gap = od - sd
        if gap > best_gap:
            best_gap = gap
            best_r = (rx, ry)
        if od < opp_min_d:
            opp_min_d = od
            closest_to_opp = (rx, ry)

    # Strategy switch: if opponent is winning races broadly, pursue their nearest resource (interceptor).
    # Otherwise, take our best race.
    if best_gap < 0:
        target = closest_to_opp
    else:
        target = best_r

    tx, ty = int(target[0]), int(target[1])

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_d = dist(nx, ny, tx, ty)
        opp_d = dist(ox, oy, tx, ty)

        # Prefer reducing our distance to target; add a small term to keep opponent farther from it.
        val = (-self_d) + (opp_d - self_d) * 0.2

        # Secondary tie-breaker: avoid stepping into being blocked by adjacency to obstacles.
        adj_obs = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj_obs += 1
        val -= adj_obs * 0.05

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]