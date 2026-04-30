def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    resources = [tuple(r) for r in observation.get("resources", []) if tuple(r) not in obstacles]
    if resources:
        dmin = None
        target = None
        for r in resources:
            d = abs(r[0] - sx) + abs(r[1] - sy)
            if dmin is None or d < dmin or (d == dmin and r < target):
                dmin = d
                target = r
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = valid[0]
    bestv = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_own = man((nx, ny), target)
        d_opp_now = man((ox, oy), target)
        d_opp_move = man((sx, sy), target)  # baseline for opponent; stable cheap term
        opp_dist = man((nx, ny), (ox, oy))
        v = -d_own
        if resources:
            # Prefer getting closer than the opponent relative to the target
            v += 0.6 * (man((sx, sy), target) - d_own)
            v -= 0.25 * (d_opp_now - d_opp_move)
        # Avoid being too close to opponent
        if opp_dist == 0:
            v -= 1000
        elif opp_dist == 1:
            v -= 20
        elif opp_dist == 2:
            v -= 5
        # Small bias toward reducing distance to opponent to contest when safe
        v += 0.05 * opp_dist
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]