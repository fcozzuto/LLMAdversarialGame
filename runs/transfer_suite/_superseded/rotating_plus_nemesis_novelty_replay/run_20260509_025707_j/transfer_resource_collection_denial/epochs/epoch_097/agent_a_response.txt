def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    # Deterministic global target (used only for a fallback/tie-break).
    target = None
    bestsd = 10**9
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        if sd < bestsd or (sd == bestsd and (rx, ry) < target):
            bestsd = sd
            target = (rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    best_tie = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Interception metric: prefer states where we are closer than opponent to some resource.
        # value = max_r(opp_dist_to_r - self_dist_to_r)
        mv = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            v = od - sd
            if v > mv:
                mv = v

        # Tie-break: prefer smaller self distance to the global target, then lexicographic.
        tie = man(nx, ny, target[0], target[1]) if target else 0
        if mv > best_val or (mv == best_val and (tie < best_tie or (tie == best_tie and (dx, dy) < (best_move[0], best_move[1])))):
            best_val = mv
            best_tie = tie
            best_move = [dx, dy]

    return best_move